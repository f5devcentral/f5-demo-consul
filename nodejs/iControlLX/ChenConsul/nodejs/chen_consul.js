/**
* A simple iControl LX extension that handles only HTTP GET
*/

function ChenConsul() {}

ChenConsul.prototype.WORKER_URI_PATH = "/shared/chen_consul/";
ChenConsul.prototype.isPublic = true;

var logger = require('f5-logger').getInstance();

/**
* handle onGet HTTP request
*/
ChenConsul.prototype.onGet = function(restOperation) {

  var query = restOperation.getUri().query;
  var options = {'host':query.host};
  var consul = require('consul')(options);

  var that = this;
  var output="";

  consul.catalog.service.nodes(query.service, function(err, result) {
  if (!err) {
    output = result.map(x => x.Address+':'+x.ServicePort).join(" ");
  } else {
    logger.error("[ChenConsul]: " + err);
  }
//  logger.info(output);
  restOperation.setBody(output);
  that.completeRestOperation(restOperation);
});

};

/**
* handle /example HTTP request
*/
ChenConsul.prototype.getExampleState = function () {
  return {
    "value": "your_string"
  };
};

module.exports = ChenConsul;
