{ pkgs ? import <nixpkgs> {}
, lib  ? pkgs.lib
, pythonPackages ? pkgs.python36Packages
}:

with pythonPackages;

let
  pytest-cov = callPackage ./pytest-cov.nix {
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
  nativeBuildInputs = [ sphinx ];
  checkInputs = [ pytest pytest-cov flake8 mypy ];
  checkPhase = ''flake8 && mypy steinbit tests'';
  propagatedBuildInputs = [
    numpy
    pytest
    scipy
    wheel
  ];
}
