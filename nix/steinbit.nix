{ pkgs ? import <nixpkgs> {}
, lib  ? pkgs.lib
, pythonPackages ? pkgs.python36Packages
}:

with pythonPackages;

let
  pytest-cov = callPackage ./pytest-cov.nix {
    pythonPackages = pythonPackages;
  };
  lasio = callPackage ./lasio.nix {
    pythonPackages = pythonPackages;
  };
  m2r2 = callPackage ./m2r2.nix {
    pythonPackages = pythonPackages;
  };
in
buildPythonPackage rec {
  pname = "steinbit";
  version = "0.1.0";
  src = ../.;
  preInstall = ''
    sphinx-build docs/source $out/html
    pytest
    mv htmlcov $out/htmlcov
  '';
  nativeBuildInputs = [ sphinx m2r2 ];
  checkInputs = [ pytest pytest-cov flake8 mypy ];
  checkPhase = ''flake8 && mypy steinbit tests'';
  propagatedBuildInputs = [
    m2r2
    lasio
    numpy
    pytest
    pandas
    scipy
    scikitlearn
    wheel
    pillow
    tqdm
  ];
}
