{ lib, pythonPackages }:

with pythonPackages;

buildPythonPackage rec {
  pname = "lasio";
  version = "0.28";

  src = fetchPypi {
    inherit pname version;
    sha256 = "18dh9x0ld082i5xqnara2j6d42vbrsrykp2969sfs8hcdzsbx3bx";
  };

  doCheck = false;
  buildInputs = with pythonPackages; [ setuptools_scm ];
  propagatedBuildInputs = with pythonPackages; [ numpy setuptools ];
}
