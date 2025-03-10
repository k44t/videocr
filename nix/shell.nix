{ pkgs ? import <nixpkgs> {} , ... }:let
  
  py = pkgs.python3.withPackages (ps: with ps; [ 
    (pkgs.python3Packages.callPackage ./python-package.nix {}) 
  ]);

in

pkgs.mkShell {

  
  buildInputs = with pkgs; [ 
    (pkgs.callPackage ./package.nix {}) 
    py
  ];
}