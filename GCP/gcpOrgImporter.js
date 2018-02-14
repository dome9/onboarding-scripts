var utils = require('./utils')
var program = require('commander');
var assert = require('assert');
program
  .option('-p, --path <path>', 'service account key path for google cloud account')
  .option('-i, --id <id>', 'API key ID for Dome9')
  .option('-s, --secret <secret>', 'API key secret for Dome9')
  .parse(process.argv);

assert(program.path,"--path is a mandatory parameter");
assert(program.id,"--id is a mandatory parameter");
assert(program.secret,"--secret is a mandatory parameter");

var google = require('googleapis');
var cloudresourcemanager = google.cloudresourcemanager('v1');
// First I want to read the file
var key = require(program.path);
var jwtClient = new google.auth.JWT(
  key.client_email,
  null,
  key.private_key,
  ['https://www.googleapis.com/auth/cloud-platform'],
  null
);

var auth = {
  username : program.id,
  password : program.secret
};
var d9Url = 'https://api.dome9.com/v2/GoogleCloudAccount';

jwtClient.authorize(function (err, tokens) {
  if (err) {
    console.log(err);
    return;
  }
  var request = {
    // TODO: Change placeholders below to appropriate parameter values for the 'list' method:
    // Auth client
    auth: jwtClient
  };
  
  var handleResultPage = function(err, result) {
    if (err) {
      console.log(err);
    } else {
      // console.log(result);
      var counter=0;
      var withFailure = false;
      result.projects.forEach(function(acc){
        var currentKey = utils.clone(key);
        currentKey.project_id = acc.projectId;
        console.log('adding project: ',currentKey.project_id);
        var options = {
          url: d9Url,
          method: 'POST',
          body: {
           name:currentKey.project_id,
            serviceAccountCredentials: currentKey
          },
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36',
            'Content-Type': 'application/json; charset=UTF-8',
            'Accept': 'application/json, text/plain, */*'
          },
          json: true
        };
        utils.simpleReq(options,auth).then(function(res){
          counter++;
          console.log('Project added successfully',res);
        })
          .catch(function(err){
            counter++;
            withFailure = true;
            console.error(err);
          })
          .finally(function(){
            if(counter == result.projects.length && !withFailure){
              process.exit(0)
            }
            else if(counter == result.projects.length && withFailure){
              process.exit(1)
            }
          })
      });
      if (result.nextPageToken) {
        request.pageToken = result.nextPageToken;
        cloudresourcemanager.projects.list(request, handleResultPage);
      }
    }
  };

  cloudresourcemanager.projects.list(request, handleResultPage);
});
