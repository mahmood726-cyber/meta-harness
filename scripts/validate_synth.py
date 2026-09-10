"""Validate harness.synth.pool_rr against metafor 5.0.1 on metafor's dat.bcg.

Runs Rscript to fit rma(measure="RR", method="PM", test="knha") and predict(),
dumps the raw 2x2 counts and metafor's log-scale results as JSON, then pools the
same counts with our engine and compares every metric. Exit 0 iff all agree within
tolerance. (dat.bcg is over-dispersed, so the HKSJ floor is inactive and our knha CI
must equal metafor's exactly; the floor's under-dispersed branch is a documented,
deliberate deviation and is unit-tested separately, not against metafor.)
"""
import json
import math
import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from harness.synth import Study, pool_rr  # noqa: E402

R_CODE = r'''
suppressMessages(library(metafor))
dat <- dat.bcg
res <- rma(measure="RR", ai=tpos, bi=tneg, ci=cpos, di=cneg, data=dat,
           method="PM", test="knha", control=list(tol=1e-12, maxiter=100000))
pr <- predict(res)
counts <- paste0('[', paste(sprintf(
  '{"label":"%s","ai":%d,"n1i":%d,"ci":%d,"n2i":%d}',
  paste(dat$author, dat$year), dat$tpos, dat$tpos+dat$tneg, dat$cpos, dat$cpos+dat$cneg),
  collapse=','), ']')
cat(sprintf(
 '{"tau2":%.12f,"mu_log":%.12f,"se_log":%.12f,"ci_lb":%.12f,"ci_ub":%.12f,"pi_lb":%.12f,"pi_ub":%.12f,"k":%d,"counts":%s}',
 res$tau2, res$beta[1], res$se, res$ci.lb, res$ci.ub, pr$pi.lb, pr$pi.ub, res$k, counts))
'''


def run_r():
    with tempfile.NamedTemporaryFile("w", suffix=".R", delete=False) as f:
        f.write(R_CODE)
        path = f.name
    try:
        out = subprocess.check_output(["Rscript", "--vanilla", path], text=True)
    finally:
        os.unlink(path)
    return json.loads(out)


def main():
    r = run_r()
    studies = [Study(**c) for c in r["counts"]]
    res = pool_rr(studies)

    got = {
        "tau2": res.tau2,
        "mu_log": res.mu_log,
        "se_log": res.se_log,
        "ci_lb": math.log(res.ci_low),
        "ci_ub": math.log(res.ci_high),
        "pi_lb": math.log(res.pi_low),
        "pi_ub": math.log(res.pi_high),
    }
    tol = 1e-6
    print(f"k: ours={res.k} metafor={r['k']}")
    ok = (res.k == r["k"])
    print(f"{'metric':10} {'ours':>16} {'metafor':>16} {'|diff|':>12}")
    for key in ("tau2", "mu_log", "se_log", "ci_lb", "ci_ub", "pi_lb", "pi_ub"):
        diff = abs(got[key] - r[key])
        flag = "OK" if diff < tol else "FAIL"
        if diff >= tol:
            ok = False
        print(f"{key:10} {got[key]:16.10f} {r[key]:16.10f} {diff:12.2e} {flag}")
    print("\nRESULT:", "PASS (all < 1e-6)" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
