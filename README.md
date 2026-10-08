# Skills MD library data

The setup guides shown in the library at [www.skillsmd.tech](https://www.skillsmd.tech/library), one for every repo and skill covered in the Skills MD newsletter.

- `issues/`: the source, one file per newsletter issue.
- `index.json` and `guides/`: built from `issues/` with `python3 build.py`. The site reads these.
- `GUIDES.md`: how the guides are written.

Each guide is written from the project's own README on the date shown in its `checked` field. Projects change, so check the project's page before you install anything. Install third-party tools at your own risk.
