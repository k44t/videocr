{
  lib,
  writeShellScript,
  bash,
  python3Packages,
  stdenv,
  python3
}:
let
  py = python3.withPackages (ps: with ps; [ 
    (python3Packages.callPackage ./python-package.nix {}) 
  ]);
in 
stdenv.mkDerivation {
  name = "videocr";
  version = "2.0";

  unpackPhase = ":";

  postInstall = ''
    mkdir -p $out/bin
    cp ${writeShellScript "videocr" ''
      #!${bash}/bin/bash
      ${py}/bin/python -m videocr.main "$@"
    ''} $out/bin/videocr
  '';
}