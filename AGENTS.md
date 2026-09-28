# Project development rules

- Deliver work incrementally and stop after each agreed stage for user review.
- Every new method must ship with a dedicated Markdown document in `docs/` and an entry in `docs/overview.md`.
- Follow [the algorithm documentation standard](docs/dev/documentation_standard_zh.md), including mathematics, limitations, variants/timing, actual library calls, and validation.
- Keep documentation synchronized with implementation; distinguish planned features from implemented capabilities.
- Prefer small functions and shared components only where duplication exists. Do not add autoplay; manual replay is intentional.
- Include an English commit message suggestion with completed changes; do not commit automatically.
