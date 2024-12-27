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
          labels: ["Offline", "Online","Never Seen"],
          datasets: [{
              data: [d_status.offline, d_status.online, d_status.never_seen],
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

  $(function() {
    console.log("Alerts:",alerts);
    // Function to create a dynamic alert card
    function createAlertCard(device, gateway, issue) {
      return `
         <div class="col-sm-4 grid-margin">
          <div class="card" style=" background-color:rgb(97, 7, 7);">
            <div class="card-body">
              <h5>${device}</h5>
              <div class="d-flex d-sm-block d-md-flex align-items-center justify-content-between">
                <h3 class="mb-0">${issue}</h3>
                <div class="d-flex justify-content-end">
                  <i class="icon-lg fa fa-exclamation text-warning"></i>
                </div>
              </div>
              <h6 class="text-muted font-weight-normal">${gateway}</h6>
            </div>
          </div>
        </div>
      `;
    }

    // Function to chunk the alerts into groups of 3
    function chunkAlerts(arr, size) {
      const result = [];
      for (let i = 0; i < arr.length; i += size) {
        result.push(arr.slice(i, i + size));
      }
      return result;
    }

    // Function to create and add rows to the container
    function addRowsToContainer() {
      $('#dynamic-rows').empty();  // Clear the container before adding new rows

      // Chunk the alerts into groups of 3
      const chunkedAlerts = chunkAlerts(alerts, 3);

      // Loop through the chunked alerts and create rows with 3 cards per row
      chunkedAlerts.forEach(chunk => {
        let rowHtml = '<div class="row">';  // Start a new row

        // Loop through each item in the chunk and create a card
        chunk.forEach(item => {
          const [device, gateway, issue] = item;  // Unpack the tuple
          const cardHtml = createAlertCard(device, gateway, issue);  // Create the card HTML
          rowHtml += cardHtml;  // Add the card to the row
        });

        rowHtml += '</div>';  // Close the row
        $('#dynamic-rows').append(rowHtml);  // Append the row to the container
      });
    }

    // Call the function to add rows when the page loads or on some event
    addRowsToContainer();  // Add rows on page load
  });

})(jQuery);
