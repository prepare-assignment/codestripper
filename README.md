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
comment:
  description: Symbol used as comment
  required: false
  default: "//"
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