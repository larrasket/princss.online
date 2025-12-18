var timeline;

var hsv2rgb = function (H, S, V) {
  var R, G, B, C, Hi, X;

  C = V * S;
  Hi = Math.floor(H / 60); // hi = 0,1,2,3,4,5
  X = C * (1 - Math.abs(((H / 60) % 2) - 1));

  switch (Hi) {
    case 0:
      R = C;
      G = X;
      B = 0;
      break;
    case 1:
      R = X;
      G = C;
      B = 0;
      break;
    case 2:
      R = 0;
      G = C;
      B = X;
      break;
    case 3:
      R = 0;
      G = X;
      B = C;
      break;
    case 4:
      R = X;
      G = 0;
      B = C;
      break;
    case 5:
      R = C;
      G = 0;
      B = X;
      break;

    default:
      R = 0;
      G = 0;
      B = 0;
      break;
  }

  return (
    "RGB(" +
    parseInt(R * 255) +
    "," +
    parseInt(G * 255) +
    "," +
    parseInt(B * 255) +
    ")"
  );
};

// Called when the Visualization API is loaded.
function drawVisualization() {
  // Create and populate a data table.

  var maxNum = 20;

  var mydata = JSON.parse(data);

  var startIdx = Math.max(mydata.length - 400, 0); // Get the starting index for the last 400 records

  // mydata = mydata.slice(startIdx); // Get the last 400 records

  var res = [];

  mydata.forEach(function (item) {
    var start = new Date(item["Start"]);
    var end = new Date(item["End"]);

    // create item with minimum requirement
    var num = item["Total"] / 6e10;

    if (num <= 0) {
      return;
    }

    num = Number(num).toFixed(2);

    var height = Math.round((num / maxNum) * 80 + 20); // a percentage, with a lower bound on 20%
    var style = "height:" + height + "px;";
    var requirement =
      '<div class="requirement" style="' +
      style +
      '" ' +
      'title="Minimum requirement: ' +
      num +
      ' minutes"></div>';

    // create item with actual number
    var num2 = Math.round(num / 60); // number of members available
    height = Math.round((num2 / maxNum) * 70 + 20); // a percentage, with a lower bound on 20%
    var hue = Math.min(Math.max(height, 20), 80) * 1.2; // hue between 0 (red) and 120 (green)

    if (item["Type"] == "sleep") {
      hue = 120;
      requirement =
        '<div class="requirement" style="' +
        style +
        '" ' +
        'title="Sleep time: ' +
        num / 60 +
        ' hours"></div>';
    } else if (item["Type"] == "awake") {
      hue = 60;

      requirement =
        '<div class="requirement" style="' +
        style +
        '" ' +
        'title="awake time: ' +
        num +
        " minutes" +
        ' minutes"></div>';
    } else if (item["Type"] == "unkown") {
      requirement =
        '<div class="requirement" style="' +
        style +
        '" ' +
        'title="Sleep time: ' +
        num / 60 +
        " uncertain hours" +
        ' hours"></div>';
      hue = 0;
    }

    var color = hsv2rgb(hue, 0.95, 0.95);

    var borderColor = hsv2rgb(hue, 0.9, 0.9);
    style =
      "height:" +
      height +
      "px;" +
      "background-color: " +
      color +
      ";" +
      "border-top: 2px solid " +
      borderColor +
      ";";
    var actual =
      '<div class="bar" style="' +
      style +
      '" ' +
      ' title="Actual: ' +
      num / 60 +
      ' hours">' +
      num +
      "</div>";

    var hue = Math.min(Math.max(height, 20), 80) * 1.2; // hue between 0 (red) and 120 (green)

    if (item["Type"] == "sleep") {
      actual =
        '<div class="bar" style="' +
        style +
        '" ' +
        ' title="Actual: ' +
        num / 60 +
        ' hours">' +
        Number(num / 60).toFixed(1) +
        " hours " +
        "</div>";
    } else if (item["Type"] == "awake") {
      hue = 120;
      actual =
        '<div class="bar" style="' +
        style +
        '" ' +
        ' title="Actual: ' +
        num / 60 +
        ' hours">' +
        Number(num).toFixed(1) +
        " minutes " +
        "</div>";
    } else if (item["Type"] == "unkown") {
      hue = 120;
      actual =
        '<div class="bar" style="' +
        style +
        '" ' +
        ' title="Actual: ' +
        num / 60 +
        ' uncertain hours">' +
        Number(num / 60).toFixed(1) +
        " uncertain hours " +
        "</div>";
    }

    var item = {
      group: "hours",
      start: start,
      end: end,
      content: requirement + actual,
    };

    res.push(item);
  });

  // specify options
  var options = {
    width: "100%",
    height: "300px",
    style: "box",
    stackEvents: false,
  };

  // Instantiate our timeline object.
  timeline = new links.Timeline(document.getElementById("mytimeline"), options);

  // Draw our timeline with the created data and options
  timeline.draw(res);
  timeline.zoom(100);
  timeline.zoom(31);
}
