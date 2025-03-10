{ pkgs ? import <nixpkgs> {} , ... }:

(pkgs.python312Packages.callPackage ./python-package.nix {}) 