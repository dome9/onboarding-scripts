/**
 * Created by arikb on 22/09/2016.
 */
var rp = require('request-promise');
var Q = require('q');
var _ = require('lodash');
var reqList = [];
var logger = console;

function loadFromFile(filename) {
  var fs = require('fs');
  var file = filename;
  var newdata = fs.readFileSync(file, 'utf8');
  return newdata;
};

function simpleReq(requestOptions,auth){
  var re = null;
  var auth = "Basic " + new Buffer(auth.username + ":" + auth.password).toString("base64");
  requestOptions.headers['Authorization'] = auth;
  // replace the url in case of v2 api.

  return insertNewReq(requestOptions).then(function (data) {
    return data;
  }, function (reason) {
    if (reason.statusCode == 504) {
      requestOptions.resolveWithFullResponse = false;
      logger.warn('got error trying to perform request: ' + JSON.stringify(requestOptions));
      logger.warn('error was: ' + JSON.stringify(reason));
      logger.warn('retrying request');
      return insertNewReq(requestOptions);
    } else {
      throw reason;
    }
  })
}

function sendRequest (requestOptions,target){
  var re = null;
  var auth = "Basic " + new Buffer(template.apiKey.id + ":" + template.apiKey.secret).toString("base64");
  requestOptions.headers['Authorization'] = auth;
  // replace the url in case of v2 api.

  requestOptions.url = "https://api.dome9.com/v2/"+target;
  return insertNewReq(requestOptions).then(function (data) {
    return data;
  }, function (reason) {
    if (reason.statusCode == 504) {
      requestOptions.resolveWithFullResponse = false;
      logger.warn('got error trying to perform request: ' + JSON.stringify(requestOptions));
      logger.warn('error was: ' + JSON.stringify(reason));
      logger.warn('retrying request');
      return insertNewReq(requestOptions);
    } else {
      throw reason;
    }
  })
}

var insertNewReq = function (reqOpts) {
  var deferred =  Q.defer();
  reqList.push({
    data: reqOpts,
    deferred: deferred
  });

  return deferred.promise;
};

function clone(obj) {
  if (null == obj || "object" != typeof obj) return obj;
  var copy = obj.constructor();
  for (var attr in obj) {
    if (obj.hasOwnProperty(attr)) copy[attr] = obj[attr];
  }
  return copy;
}

// Queue requests to avoid being throthled by the system. 
global.setInterval(function () {
  var currentReq = reqList.shift();
  if(currentReq){
    //console.log('currentReq',currentReq)
      (currentReq.data).then(function(data){
      this.deferred.resolve(data);
    }.bind(currentReq), function(reason){
      this.deferred.reject(reason);
    }.bind(currentReq));
  }
}, 1500);

module.exports ={
  sendRequest:sendRequest,
  loadFromFile:loadFromFile,
  simpleReq:simpleReq,
  clone:clone
}