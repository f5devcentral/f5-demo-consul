/**
* A simple iControl LX extension that handles only HTTP GET
*/

function DemoConsul() {
  this.state = {};
}

DemoConsul.prototype.WORKER_URI_PATH = "/shared/demo/consul";
DemoConsul.prototype.isPublic = true;

var logger = require('f5-logger').getInstance();
/**
* handle onGet HTTP request
*/
DemoConsul.prototype.onGet = function(restOperation) {
  restOperation.setBody(this.state);
  this.completeRestOperation(restOperation);  
};
/**
* handle onPost HTTP request
*/
DemoConsul.prototype.onPost = function(restOperation) {

  var query = restOperation.getUri().query;
  var post = restOperation.getBody();
//  logger.info(post);
//  logger.info(post.service);
  var options = {'host':post.host};
  var consul = require('consul')(options);

  var that = this;
  var output="";

  consul.catalog.service.nodes(post.service, function(err, result) {
  if (!err) {
    output = result.map(x => x.Address+':'+x.ServicePort);
    output.sort();
    output = output.join(" ");
  } else {
    logger.error("[DemoConsul]: " + err);
    output = JSON.stringify({"error":"" + err});
  }
//  logger.info(output);  
  restOperation.setBody(output);
  that.completeRestOperation(restOperation);
});

};

/**
* handle /example HTTP request
*/
DemoConsul.prototype.getExampleState = function () {
  return {
    "host": "Consul Host [Required]",
    "service": "Consul Service [Required]"
  };
};

module.exports = DemoConsul;
