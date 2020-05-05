(function () {
  	'use strict';

  	angular.module('rxkcdApp', [])

    .controller('rxkcdController', ['$scope', '$log', '$http', '$timeout',
		function($scope, $log, $http, $timeout) {

			$scope.showResults = function(stype, query) {
			    var timeout = "";
			    $log.log(stype);
			    $log.log(query);
			    var poller = function() {
				    $http.get('/results/'+stype+'/'+query).
				        success(function(data, status, headers, config) {
				        if(status === 202) {
				            $log.log(data, status);
				        } else if (status === 200){
				            $log.log(data);
				            $timeout.cancel(timeout);
				            window.location.replace('/search/'+stype+'/'+query);
				            return false;
				        }
				        timeout = $timeout(poller, 5000);
				    	}).
					    error(function(error) {
					    	$log.log(error);
					    });
			    };
			    poller();
			}
		}
	]);
}());

