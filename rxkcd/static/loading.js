(function () {
  	'use strict';

  	angular.module('rxkcdApp', [])

    .controller('rxkcdController', ['$scope', '$log', '$http', '$timeout',
		function($scope, $log, $http, $timeout) {

			$scope.showResults = function(query) {
			    var timeout = "";
			    $log.log(query);
			    var poller = function() {
				    $http.get('/results/'+query).
				        success(function(data, status, headers, config) {
				        if(status === 202) {
				            $log.log(data, status);
				        } else if (status === 200){
				            $log.log(data);
				            $timeout.cancel(timeout);
				            window.location.replace('/search/'+query);
				            return false;
				        }
				        timeout = $timeout(poller, 2000);
				    	}).
					    error(function(error) {
					    	$log.log(error);
				            $timeout.cancel(timeout);
					    });
			    };
			    poller();
			}
		}
	]);
}());

