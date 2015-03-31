/* Author: Aptuz
*/


mainApp.constant("appConstants", {
    'homePath': '/',
    'loginPath': '/login/',
    'apiPath' : '/api/',
    'templateDir' : 'partials/',
    'imageDir' : 'images/',
});

/* Partial Routes */
mainApp.constant("urlRoutes", [
    {'path':'/','templatePath':'home.html','controller':'HomeController'},
]);

//Filters
mainApp.filter('range', function() {
    return function(input, total) {
        total = parseInt(total);
        for (var i=0; i<total; i++)
            input.push(i);
        return input;
    };
});

//base Controller
mainApp.controller('baseController',['$scope','Constants','$location','growl','$http','$timeout', '$modal', 'loadTemplate',
    function($scope,Constants,$location,growl,$http,$timeout,$modal,loadTemplate){        
        $scope.username = Constants.get("userSiteObj")['username'];
		
}]).directive('enter',function($document){
    return function(scope,elem,attrs){
        $("body").on('keyup',function(e) {
           if(e.keyCode == 13){
                if($(".active").text() == "Sign-In"){
                    $("input[value='Sign In']").trigger('click');
                }
                else{
                    $("input[value='Join Feazt']").trigger('click');
                }
           }
        });
    }
}).directive('dropdown',function($document){
    return function(scope,elem,attrs){
        $(document.body).on('click', function (e) {
            var obj = e.target;
            if (!$(obj).hasClass('dropdown-handler--name') && !$(obj).hasClass('dropdown-handler')) {
                if (!$(".dropdown-list").hasClass("hide")) {
                    $(".dropdown-list").addClass("hide");
                }
            }
        });
        $(".dropdown-handler").on('click',function(e) {
            $(".dropdown-list").toggleClass("hide");
        });
    }
}).directive('dropdownnoty',function($document){
    return function(scope,elem,attrs){
        $(document.body).on('click', function (e) {
            var obj = e.target;
            if (!$(obj).hasClass('noty-wrap') && !$(obj).hasClass('fa-bell')) {
                if (!$(".noty-req-wrap").hasClass("hide")) {
                    $(".noty-req-wrap").addClass("hide");
                }
            }
        });
        $(".noty-wrap").on('click',function(e) {
            $(".noty-req-wrap").toggleClass("hide");
        });

    }
});

mainApp.controller('HomeController',['$scope','Constants','$location','growl','$http','$timeout','transformRequestAsFormPost','$modal','loadTemplate',
    function($scope,Constants,$location,growl,$http,$timeout,transformRequestAsFormPost, $modal, loadTemplate){ 
        $scope.user_id = parseInt(Constants.get("userSiteObj")["pk"]);
        
        $scope.activeMenu = "grid";

        var options = {
            'method': 'GET',
            'url': Constants.get('apiPath') + "usersubscriptions/"
        };
        
        $http(options).success(function(data){
            console.log(data);
            $scope.Subscriptions = data;
        });

        var options = {
            'method': 'GET',
            'url': Constants.get('apiPath') + "feeds/"
        };
        
        $http(options).success(function(data){
            $scope.Feeds = data;
            console.log(data);
        });

        $scope.unsubscribe = function(Subscription){
            alert("asdf");
        };

        $scope.activeFeed = '';
        $scope.setActiveFeed = function(feed){
            $scope.activeFeed = feed.pk;
        }
        //Adding a feed
        $scope.addWebsite = function(url){
            var modalInstance = $modal.open({
                templateUrl: loadTemplate(Constants.get('staticLink'),Constants.get('templateDir'),'add_website.html'),
                backdrop: true,
                controller: function($scope,$modalInstance){
                    $scope.cancel = function () {
                        $modalInstance.dismiss('cancel');
                    };

                    $scope.addSubscription = function(feed){
                        console.log(feed);
                        var options = {
                            'method': 'GET',
                            'url': Constants.get('apiPath') + "usersubscriptions/?feeds="+feed,
                        };

                        $http(options).success(function(data){
                            console.log(data);
                            if(data.length == 0){
                                var options = {
                                    'method': 'POST',
                                    'transformRequest':transformRequestAsFormPost,
                                    'url': Constants.get('apiPath') + "usersubscriptions/",
                                    'data': {'feeds':feed }
                                };
                                
                                $http(options).success(function(data){
                                    console.log(data);
                                    $modalInstance.dismiss('cancel');
                                }).error(function(data){
                                    console.log(data);
                                });
                            }
                            else {
                                alert("You've already subscribed");
                                $modalInstance.dismiss('cancel');
                            }
                        });
                    };

                    $scope.getFeedMapper = function(data){
                        var options = {
                            'method': 'GET',
                            'url': Constants.get('apiPath') + "feedmapper/?url="+data.url,
                        };
                        
                        $http(options).success(function(result){
                            console.log(result);
                            if(result.length > 0)
                            {
                                console.log(result);
                                $scope.addSubscription(result[0].id);
                            }
                            else{
                                $scope.addFeedMapper(data);
                            }
                        });
                    };

                    $scope.addFeedMapper = function(data){
                        var options = {
                            'method': 'POST',
                            'transformRequest':transformRequestAsFormPost,
                            'url': Constants.get('apiPath') + "feedmapper/",
                            'data': data
                        };
                        
                        $http(options).success(function(data){
                            console.log(data);
                            $scope.addSubscription(data.result.id);
                        }).error(function(data){
                            console.log(data);
                        });
                    };

                    $scope.getFeedUrl = function(){
                        var options = {
                            'method': 'POST',
                            'transformRequest':transformRequestAsFormPost,
                            'url': "/get_feed_url/",
                            'data': {'url':$scope.websiteurl}
                        };
                        
                        $http(options).success(function(data){
                            if(data.message == "Feed url found"){
                                $scope.websiteurl = data.url;
                                $scope.feedurl = data.feedurl;
                                //add to feed mapper
                                $scope.getFeedMapper({'url':data.url, 'feed_url':data.feedurl});
                            } else alert(data.message);
                        });
                    };
                },
                size: 'md',
                resolve: {
                }
            });
            modalInstance.result.then(function () {
                
            }, function () {
                // $log.info('Modal dismissed at: ' + new Date());
            });
            
        };

}]);



mainApp.controller('accountsController',['$scope','Constants','$location','growl','$http','$timeout', 'transformRequestAsFormPost',
    function($scope,Constants,$location,growl,$http,$timeout, transformRequestAsFormPost){        
        
        $scope.login = function ($event, lname, lpwd) {
            $event.target.setAttribute('disabled', 'disabled');
            var options = {
                'transformRequest': transformRequestAsFormPost,
                'method': 'POST',
                'url': '/login/',
                'data': {
                    'username': lname,
                    'password': lpwd,
                }
            };
            $http(options).success(function (data) {
                if (data.message === "success") {
                    window.location.href = "/";
                }
            }).error(function (data) {
                $event.target.removeAttribute('disabled');
            });
        };

        $scope.register = function ($event, rname, remail, rpwd) {
            $event.target.setAttribute('disabled', 'disabled');
            var options = {
                'transformRequest': transformRequestAsFormPost,
                'method': 'POST',
                'url': '/register/',
                'data': {
                    'username': rname,
                    'email': remail,
                    'password': rpwd,
                }
            };
            $http(options).success(function (data) {
                if (data.message === "success") {
                    window.location.href = "/";
                }
            }).error(function (data) {
                $event.target.removeAttribute('disabled');
            });
        };
}]);







