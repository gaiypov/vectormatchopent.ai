{ pkgs }: {
  deps = [
    pkgs.python39Full
    pkgs.python39Packages.pip
    pkgs.python39Packages.setuptools
    pkgs.python39Packages.wheel
  ];
}
