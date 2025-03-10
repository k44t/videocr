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
  version = "2.0";
  pyproject = true;

  src = ./..;
  
  /*src = fetchPypi {
    inherit pname version;
    hash = "sha256-w0hPfUK4un5JAjAP7vwOAuKlsZ+zv6sFV2vD/Rl3kbI=";
  };*/

  build-system = [ setuptools ];

  dependencies = deps;

  # Project has no tests
  doCheck = false;

  pythonImportsCheck = [ "videocr" ];

  meta = with lib; {
    description = "Extract hardcoded subtitles from videos using machine learning";
    homepage = "https://github.com/k44t/videocr";
    license = licenses.mit;
    maintainers = with maintainers; [ ];
  };
}
