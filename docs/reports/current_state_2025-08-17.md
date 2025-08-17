# Current State Repo Snapshot

Generated: 2025-08-17T04:20:23Z

## Summary

- HEAD: 626e44eae4a48d59083581a672956ba64425de52
- Branch: docs/retire-track-b-proposer-2025-08-16
- Title: Fill Memory Card: Track C Manual Test (2025-08-14) Mem-Intent: Author-at-source: purpose=TrackC-Test; scope=Persona; status=Active
- Files tracked: 762

## Directory Map (depth 2)

- .devcontainer: 2 files; subdirs: Dockerfile, devcontainer.json
- .github: 4 files; subdirs: ISSUE_TEMPLATE, workflows
- .gitignore: 1 files; subdirs: 
- .venv: 493 files; subdirs: bin, lib, lib64, pyvenv.cfg
- .vscode: 1 files; subdirs: tasks.json
- CHANGELOG.md: 1 files; subdirs: 
- Downloads: 1 files; subdirs: chatgpt-export.zip
- README.md: 1 files; subdirs: 
- archives: 5 files; subdirs: chat_exports
- backup.py: 1 files; subdirs: 
- charlotte_core: 75 files; subdirs: README.md, _intake, charlotte_backup_process.md, charlotte_ops.md, compliance, core_context, developer_mind, draft_Charlotte3_v1.md, modes, persona
- config.example.yaml: 1 files; subdirs: 
- config.yaml: 1 files; subdirs: 
- docs: 5 files; subdirs: charlotte_ai_prd.md, charlotte_memory_pipeline.md, process, prompts
- reports: 4 files; subdirs: code_review, export_ingest_2025-08-13.md
- restore_checklist.md: 1 files; subdirs: 
- scripts: 2 files; subdirs: backup.ps1, backup.sh
- snapshots: 154 files; subdirs: 2025-08-11_003602Z, 2025-08-11_003725Z
- tests: 2 files; subdirs: ingest_export_smoke.sh, test_ingest_report.py
- tools: 7 files; subdirs: __init__.py, charlotte_restore_builder.py, ingest_chatgpt_export.py, memory_card_scaffolder.py, memory_diff_proposer.py, requirements.txt, utils.py

## Key Paths Check

- charlotte_core: present
- imports/chatgpt_export: MISSING
- archives/chat_exports: MISSING
- snapshots: present
- out: MISSING

## Deprecated Scan

Matches (excluding allowed ops note): 0

## Changed Files (vs main)

No changed files detected.

## TODO / FIXME

- .venv/lib/python3.12/site-packages/pip/_internal/build_env.py:302 # FIXME: Consider direct URL?
- .venv/lib/python3.12/site-packages/pip/_internal/cache.py:280 # TODO: use DirectUrl.equivalent when
- .venv/lib/python3.12/site-packages/pip/_internal/cli/base_command.py:209 # TODO: Try to get these passing down from the command?
- .venv/lib/python3.12/site-packages/pip/_internal/commands/inspect.py:60 # TODO tags? scheme?
- .venv/lib/python3.12/site-packages/pip/_internal/index/collector.py:339 # TODO: In the future, it would be nice if pip supported PEP 691
- .venv/lib/python3.12/site-packages/pip/_internal/locations/base.py:16 # FIXME doesn't account for venv linked to global site-packages
- .venv/lib/python3.12/site-packages/pip/_internal/locations/base.py:60 # FIXME: keep src in cwd for now (it is not a temporary folder)
- .venv/lib/python3.12/site-packages/pip/_internal/metadata/base.py:32 from pip._internal.utils.compat import stdlib_pkgs  # TODO: Move definition here.
- .venv/lib/python3.12/site-packages/pip/_internal/metadata/base.py:162 # TODO: this property is relatively costly to compute, memoize it ?
- .venv/lib/python3.12/site-packages/pip/_internal/metadata/base.py:172 # TODO: get project location from second line of egg_link file
- .venv/lib/python3.12/site-packages/pip/_internal/models/installation_report.py:51 # TODO: currently, the resolver uses the default environment to evaluate
- .venv/lib/python3.12/site-packages/pip/_internal/models/selection_prefs.py:6 # TODO: This needs Python 3.10's improved slots support for dataclasses
- .venv/lib/python3.12/site-packages/pip/_internal/network/lazy_wheel.py:177 # TODO: Get range requests to be correctly cached
- .venv/lib/python3.12/site-packages/pip/_internal/operations/prepare.py:562 # TODO: separate this part out from RequirementPreparer when the v1
- .venv/lib/python3.12/site-packages/pip/_internal/operations/prepare.py:636 # FIXME: https://github.com/pypa/pip/issues/11943
- .venv/lib/python3.12/site-packages/pip/_internal/req/constructors.py:287 # TODO: The is_installable_dir test here might not be necessary
- .venv/lib/python3.12/site-packages/pip/_internal/req/req_file.py:104 # TODO: replace this with slots=True when dropping Python 3.9 support.
- .venv/lib/python3.12/site-packages/pip/_internal/req/req_file.py:256 # FIXME: it would be nice to keep track of the source
- .venv/lib/python3.12/site-packages/pip/_internal/req/req_file.py:523 # TODO: handle space after '\'.
- .venv/lib/python3.12/site-packages/pip/_internal/req/req_install.py:374 # FIXME: Is there a better place to create the build_dir? (hg and bzr
- .venv/lib/python3.12/site-packages/pip/_internal/req/req_set.py:74 TODO remove this property together with the legacy resolver, since the new
- .venv/lib/python3.12/site-packages/pip/_internal/req/req_uninstall.py:483 # FIXME: need a test for this elif block
- .venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/candidates.py:230 # TODO performance: this means we iterate the dependencies at least twice,
- .venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/candidates.py:365 # TODO: Supply reason based on force_reinstall and upgrade_strategy.
- .venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/factory.py:194 # TODO: Check already installed candidate, and use it if the link and
- .venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/factory.py:613 # TODO: Are there more cases this needs to return True? Editable?
- .venv/lib/python3.12/site-packages/pip/_internal/utils/unpacking.py:328 # FIXME: handle?
- .venv/lib/python3.12/site-packages/pip/_internal/utils/unpacking.py:329 # FIXME: magic signatures?
- .venv/lib/python3.12/site-packages/pip/_internal/vcs/subversion.py:60 # FIXME: should we warn?
- .venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/controller.py:227 # TODO: There is an assumption that the result will be a
- .venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/filewrapper.py:67 # TODO: Add some logging here...
- .venv/lib/python3.12/site-packages/pip/_vendor/distlib/util.py:401 # TODO check k, v for valid values
- .venv/lib/python3.12/site-packages/pip/_vendor/msgpack/fallback.py:499 # TODO should we eliminate the recursion?
- .venv/lib/python3.12/site-packages/pip/_vendor/msgpack/fallback.py:503 # TODO check whether we need to call `list_hook`
- .venv/lib/python3.12/site-packages/pip/_vendor/msgpack/fallback.py:511 # TODO is the interaction between `list_hook` and `use_list` ok?
- .venv/lib/python3.12/site-packages/pip/_vendor/msgpack/fallback.py:516 # TODO check whether we need to call hooks
- .venv/lib/python3.12/site-packages/pip/_vendor/packaging/metadata.py:204 # TODO: The spec doesn't say anything about if the keys should be
- .venv/lib/python3.12/site-packages/pip/_vendor/packaging/metadata.py:805 description: _Validator[str | None] = _Validator()  # TODO 2.1: can be in body
- .venv/lib/python3.12/site-packages/pip/_vendor/packaging/requirements.py:29 # TODO: Can we test whether something is contained within a requirement?
- .venv/lib/python3.12/site-packages/pip/_vendor/packaging/requirements.py:32 # TODO: Can we normalize the name and extra name?
- .venv/lib/python3.12/site-packages/pip/_vendor/packaging/tags.py:378 # TODO: Need to care about 32-bit PPC for ppc64 through 10.2?
- .venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:1 # TODO: Add Generic type annotations to initialized collections.
- .venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:122 _ResourceStream = Any  # TODO / Incomplete: A readable file-like object
- .venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:2031 # FIXME: 'ZipProvider._extract_resource' is too complex (12)
- .venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:3201 # FIXME: 'Distribution.insert_on' is too complex (13)
- .venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:3308 # TODO: remove this except clause when python/cpython#103632 is fixed.
- .venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py:3598 # TODO: Add a deadline?
- .venv/lib/python3.12/site-packages/pip/_vendor/pygments/filters/__init__.py:72 highlight ``XXX``, ``TODO``, ``FIXME``, ``BUG`` and ``NOTE``.
- .venv/lib/python3.12/site-packages/pip/_vendor/pygments/filters/__init__.py:75 Now recognizes ``FIXME`` by default.
- .venv/lib/python3.12/site-packages/pip/_vendor/pygments/filters/__init__.py:81 ['XXX', 'TODO', 'FIXME', 'BUG', 'NOTE'])
- .venv/lib/python3.12/site-packages/pip/_vendor/pygments/lexer.py:863 TODO: clean up the code here.
- .venv/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/python.py:715 # different tokens.  TODO: DelegatingLexer should support this
- .venv/lib/python3.12/site-packages/pip/_vendor/requests/adapters.py:686 # TODO: Remove this in 3.0.0: see #2811
- .venv/lib/python3.12/site-packages/pip/_vendor/requests/hooks.py:19 # TODO: response is the only one
- .venv/lib/python3.12/site-packages/pip/_vendor/rich/text.py:562 # TODO: This is a little inefficient, it is only used by full justify
- .venv/lib/python3.12/site-packages/pip/_vendor/truststore/_macos.py:558 # TODO: Not sure if we need the SecTrustResultType for anything?
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/connection.py:199 # TODO: Fix tunnel so it doesn't depend on self.sock state.
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/connectionpool.py:522 # TODO: Add optional support for socket.gethostbyname checking.
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/pyopenssl.py:371 # FIXME rethrow compatible exceptions should we ever use this
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/securetransport.py:659 # TODO: should I do clean shutdown here? Do I have to?
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/securetransport.py:819 # TODO: Well, crap.
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/securetransport.py:829 # TODO: Update in line with above.
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/exceptions.py:289 # TODO(t-8ch): Stop inheriting from AssertionError in v2.0.
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/response.py:441 # FIXME: Ideally we'd like to include the url in the ReadTimeoutError but
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/response.py:446 # FIXME: Is there a better way to differentiate between SSLErrors?
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/response.py:798 # FIXME: Rewrite this method and make it a class with a better structured logic.
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/response.py:103 # FIXME: Can we do this somehow without accessing private httplib _method?
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/retry.py:31 # TODO: In v2 we can remove this sentinel and metaclass with deprecated options.
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/retry.py:261 # TODO: Deprecated, remove in v2.0
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/retry.py:323 # TODO: If already given in **kw we use what's given to us
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/retry.py:454 # TODO: For now favor if the Retry implementation sets its own method_whitelist
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/retry.py:608 # TODO: Remove this deprecated alias in v2.0
- .venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/url.py:402 # TODO: Remove this when we break backwards compatibility.
- .venv/lib/python3.12/site-packages/yaml/scanner.py:187 # TODO: support for BOM within a stream.
- .venv/lib/python3.12/site-packages/yaml/scanner.py:761 # TODO: We need to make tab handling rules more sane. A good rule is
- snapshots/2025-08-11_003602Z/charlotte_ai/developer_mind/stack_profile.md:63 ## 📌 TODOs / Ongoing Refinement
- snapshots/2025-08-11_003725Z/charlotte_ai/developer_mind/stack_profile.md:63 ## 📌 TODOs / Ongoing Refinement

## Next Steps

- Remove any remaining proposer tooling or mark tools/memory_diff_proposer.py as deprecated (if desired)
- Add `docs/reports/current_state_<DATE>.md/.json` to CI snapshot step
- Consider a small test to assert deprecated patterns count is zero
