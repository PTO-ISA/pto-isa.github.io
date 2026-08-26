# PTO-ISA GitHub Pages

This repository is the deployment controller for <https://pto-isa.github.io/>.
It does not build or restate PTO semantics.

The deployed site is the content-addressed Docusaurus artifact produced by the
accepted `PTO-ISA/pto-spec` release workflow. ASL/NDF in that repository remains
the normative source; this repository verifies release identity and deploys the
accepted static files through GitHub Actions Pages.

The checked-in legacy HTML remains only as rollback history and is not the
active publication source after the Actions Pages cutover.
