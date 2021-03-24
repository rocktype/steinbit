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
  m2r2 = callPackage ./nix/m2r2.nix {
    pythonPackages = pythonPackages;
  };
in
  mkShell {
    buildInputs = with pythonPackages; [
      steinbit 
      python 
      sphinx     ## Documentation
      m2r2       ## ...conversion of README.md
      pytest     ## Testing
      pytest-cov ## Code coverage
      codecov    ## Code coverage upload
      flake8     ## Python code linting
      mypy       ## Python typing
      grip       ## Preview github markdown
    ];
  }
