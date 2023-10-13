# Releasing MultiTree

```shell
cldfbench makecldf cldfbench_multitree.py --glottolog-version v4.8 --with-cldfreadme
pytest
```

```shell
cldfbench readme cldfbench_multitree.py
cldfbench zenodo --communities linguistlist,cldf-datasets cldfbench_multitree.py
```

```shell
rm multitree.sqlite
cldf createdb cldf multitree.sqlite
```

```shell
cldferd --format compact.svg cldf > erd.svg
```