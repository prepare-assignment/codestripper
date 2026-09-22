# Codestripper action

This actions strips files based on certain tags. It basically is a prepare assignment action that calls the actual [codestripper](https://github.com/FontysVenlo/codestripper).

## Options

The following options are available:

```yaml
include:
  description: files to include for code stripping (glob)
  required: true
  type: array
  items: string
exclude:
  description: files to exclude for code stripping (glob)
  required: false
  type: array
  items: string
working-directory:
  description: Set the working directory of prepare_codestripper (defaults to pwd)
  required: false
  type: string
allow-outside-working-directory:
  description: Allow glob(s) to match outside the working directory
  required: false
  type: boolean
  default: false
output-directory:
  description: Output directory for stripped files
  required: false
  default: out
comments:
  description: "Comment symbols per file extension, added to (or overriding) the built-in ones: <extension>:<open>[:<close>], e.g. '.xyz:#' or '.html:<!--:-->'"
  required: false
  type: array
  items: string
recursive:
  description: Whether or not to use recursive search in the globs for files/exclude
  required: false
  type: boolean
  default: true
verbosity:
  description: Set verbosity level of output
  required: false
  type: integer
  default: 1
dry-run:
  description: Perform a dry-run, no actual files will be written
  required: false
  type: boolean
  default: false
fail-on-error:
  description: Should the action fail if an error occurs
  required: false
  type: boolean
  default: true
unknown:
  description: What to do with unknown file extensions (FAIL, IGNORE, INCLUDE)
  required: false
  type: string
  default: FAIL
binary:
  description: What to do with binary files (FAIL, IGNORE, INCLUDE)
  required: false
  type: string
  default: FAIL
```

## Outputs

The following outputs are available:

```yaml
matched-files:
  description: Files that matched the provided input glob(s)
  type: array
  items: string
stripped-files:
  description: The actual stripped files from the matched-files
  type: array
  items: string
```

## Releases

Releases are automated with [semantic-release](https://semantic-release.gitbook.io/). Pull requests are squash merged, so the PR title becomes the commit on `main` and must follow [Conventional Commits](https://www.conventionalcommits.org/) (checked on every PR):

| PR title | Release |
|----------|---------|
| `fix: ...`, `perf: ...` | patch (1.2.3 → 1.2.4) |
| `feat: ...` | minor (1.2.3 → 1.3.0) |
| `!` after the type (e.g. `feat!: ...`, `refactor!: ...`) or a `BREAKING CHANGE:` footer | major (1.2.3 → 2.0.0) |
| `docs:`, `chore:`, `ci:`, `build:`, `refactor:`, `test:`, `style:`, `revert:` | no release |

On every merge to `main` the next version is determined, tagged (`vX.Y.Z`) and a GitHub release is created. The major tag (e.g. `v1`) is moved to the new release, so `uses: codestripper@v1` always gets the newest 1.x version.

Because the major tag moves, `git pull` in an existing clone can fail with `! [rejected] v1 -> v1 (would clobber existing tag)`. Update the tags once with `git fetch --tags --force` and pull again.
