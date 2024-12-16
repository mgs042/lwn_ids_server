(function($) {
  'use strict';
  $.fn.andSelf = function() {
    return this.addBack.apply(this, arguments);
  }
  $(function() {

    if ($("#devices_donut").length) { 
      const doughnutChartCanvas = document.getElementById('devices_donut');
      new Chart(doughnutChartCanvas, {
        type: 'doughnut',
        data: {
          labels: ["Paypal", "Stripe","Cash"],
          datasets: [{
              data: [55, 25, 20],
              backgroundColor: [
                 "#111111","#00d25b","#ffab00",
              ],
              borderColor: "#191c24"
          }]
        },
        options: {
          cutout: 70,
          animationEasing: "easeOutBounce",
          animateRotate: true,
          animateScale: false,
          responsive: true,
          maintainAspectRatio: true,
          showScale: false,
          legend: false,
          plugins: {
            legend: {
                display: false,
            },
          },
        },
      });
    }
    if ($("#gateways_donut").length) { 
      const doughnutChartCanvas = document.getElementById('gateways_donut');
      new Chart(doughnutChartCanvas, {
        type: 'doughnut',
        data: {
          labels: ["Offline", "Online","Never Seen"],
          datasets: [{
              data: [g_status.offline, g_status.online, g_status.never_seen],
              backgroundColor: [
                "#cc0000", // Muted Red
                "#008000", // Dark Green
                "#ff8c00"  // Dark Orange
            ],
              borderColor: "#191c24"
          }]
        },
        options: {
          cutout: 70,
          animationEasing: "easeOutBounce",
          animateRotate: true,
          animateScale: false,
          responsive: true,
          maintainAspectRatio: true,
          showScale: false,
          legend: false,
          plugins: {
            legend: {
                display: false,
            },
          },
        },
      });
    }
    
  });
})(jQuery);
