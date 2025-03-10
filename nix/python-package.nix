{
  lib,
  buildPythonPackage,
  fetchPypi,
  setuptools,
  levenshtein,
  pytesseract,
  opencv-python,
  fuzzywuzzy,
  writeShellScript,
  bash,
  python
}:
let
deps = [
    levenshtein
    pytesseract
    opencv-python
    fuzzywuzzy
  ];
in buildPythonPackage rec {
  pname = "videocr";
  version = "master";
  pyproject = true;

  src = ./..;
  
  /*src = fetchPypi {
    inherit pname version;
    hash = "sha256-w0hPfUK4un5JAjAP7vwOAuKlsZ+zv6sFV2vD/Rl3kbI=";
  };*/

  build-system = [ setuptools ];

  dependencies = deps;

  postPatch = ''
    substituteInPlace setup.py \
      --replace-fail "python-Levenshtein" "Levenshtein"
    substituteInPlace videocr/constants.py \
      --replace-fail "master" "main"

    mkdir -p $out/bin
    cp ${writeShellScript "videocr" ''
      #!${bash}/bin/bash
      PATH=$out/bin:${lib.makeBinPath deps}:${python}/bin python3 -m videocr.main
    ''} $out/bin/videocr
  '';

  # Project has no tests
  doCheck = false;

  pythonImportsCheck = [ "videocr" ];

  meta = with lib; {
    description = "Extract hardcoded subtitles from videos using machine learning";
    homepage = "https://github.com/apm1467/videocr";
    license = licenses.mit;
    maintainers = with maintainers; [ ozkutuk ];
  };
}
