{ lib, pythonPackages }:

with pythonPackages;

buildPythonPackage rec {
  pname = "m2r2";
  version = "0.2.7";

  src = fetchPypi {
    inherit pname version;
    sha256 = "1xad55vc5yrql5hmgdin3x2i45j3hxv2dicpixjl33b4kzg2mxzv";
  };

  buildInputs = [ pytest ];
  propagatedBuildInputs = [ docutils mistune coverage ];

  doCheck = false;
  checkPhase = ''
    # allow to find the module helper during the test run
    export PYTHONPATH=$PYTHONPATH:$PWD/tests
    py.test tests
  '';

  meta = with lib; {
    description = "M2R2 converts a markdown file including reStructuredText (rst) markups to a valid rst format.";
    homepage = "https://github.com/crossnox/m2r2";
    license = licenses.mit;
  };
}
