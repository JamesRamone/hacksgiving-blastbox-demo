# slugify-lite

Lightweight, zero-dependency Python 3 utility for turning arbitrary Unicode strings into clean ASCII URL slugs.

## Install

```bash
python3 -m pip install --no-build-isolation --no-deps .
```

## Usage

```python
from slugify_lite import slugify

slugify("Café Crème & Naïve")  # -> "cafe-creme-naive"
slugify("Fly.io Hacksgiving 2026", separator="_")  # -> "fly_io_hacksgiving_2026"
```

## Testing

```bash
python3 -m unittest discover -s tests -v
```
