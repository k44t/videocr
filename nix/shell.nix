{ pkgs ? import <nixpkgs> {} , ... }:let
  
in

pkgs.mkShell {

  
  buildInputs = with pkgs; [ 
    (pkgs.python312Packages.callPackage ./python-package.nix {}) 
  ];
}