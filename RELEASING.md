# Releasing MultiTree

```shell
cldfbench makecldf cldfbench_multitree.py --glottolog-version v4.8 --with-zenodo --with-cldfreadme
pytest
```

```shell
cldfbench readme cldfbench_multitree.py
```

```shell
cldferd --format compact.svg cldf > erd.svg
```