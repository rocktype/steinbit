with import <nixpkgs> {};

let
  python = python38;
  pythonPackages = python38Packages;
  steinbit = callPackage ./nix/steinbit.nix {
    pythonPackages = pythonPackages;
  };
  pytest-cov = callPackage ./nix/pytest-cov.nix {
    pythonPackages = pythonPackages;
  };
in
  mkShell {
    buildInputs = with pythonPackages; [
      steinbit 
      python 
      sphinx     ## Documentation
      pytest     ## Testing
      pytest-cov ## Code coverage
      codecov    ## Code coverage upload
      flake8     ## Python code linting
      mypy       ## Python typing
      grip       ## Preview github markdown
    ];
  }
