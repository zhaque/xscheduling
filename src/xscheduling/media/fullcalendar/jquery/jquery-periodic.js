 jQuery.periodic = function (callback, options) { 
      callback = callback || (function() { return false; }); 
      options = jQuery.extend({ }, 
                              { frequency : 10, 
                                allowParallelExecution : false}, 
                              options); 
      var currentlyExecuting = false; 
      var timer; 
      var controller = { 
         stop : function () { 
           if (timer) { 
             window.clearInterval(timer); 
             timer = null; 
           } 
         }, 
         currentlyExecuting : false, 
         currentlyExecutingAsync : false 
      }; 
      timer = window.setInterval(function() { 
         if (options.allowParallelExecution || !(controller.currentlyExecuting || controller.currentlyExecutingAsync)) 
		 { 
            try { 
                 controller.currentlyExecuting = true; 
                 if (!(callback(controller))) { 
                     controller.stop(); 
                 } 
             } finally { 
              controller.currentlyExecuting = false; 
            } 
         } 
      }, options.frequency * 1000); 
}; 