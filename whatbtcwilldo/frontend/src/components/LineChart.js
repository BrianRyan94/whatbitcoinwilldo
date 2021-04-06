import React from "react";
import { ResponsiveLine } from "@nivo/line";
import SharedStyles from "./SharedStyles";
import Card from "@material-ui/core/Card";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";

const FormatThousand = (num) => {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
};

const LineChart = ({ dataseries, title, error }) => {
  var data;
  var xaxis_ticks;
  var xaxis_tick_count = 10;
  var yaxis_min;
  if (dataseries == null) {
    data = [];
  } else {
    dataseries = dataseries.map((row) => {
      return { x: row.dt, y: parseInt(row.trade) };
    });
    data = [{ id: "priceseries", data: dataseries }];
    let tick_increment = Math.floor(dataseries.length / xaxis_tick_count);
    xaxis_ticks = [];
    for (var i = 0; i < dataseries.length; i += tick_increment) {
      xaxis_ticks.push(dataseries[i].x);
    }
    let yaxisvalues = dataseries.map((value) => {
      return value.y;
    });

    yaxis_min = Math.min(...yaxisvalues);
  }

  const shared_style = SharedStyles();

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography className={shared_style.cardHeaders}>{title}</Typography>
        <div className={shared_style.default_chart_dim}>
          <ResponsiveLine
            data={data}
            margin={{
              top: 50,
              right: 110,
              bottom: 50,
              left: 60,
            }}
            pointSize={4}
            pointBorderWidth={2}
            pointBorderColor={{ from: "serieColor" }}
            enableArea={true}
            areaBaselineValue={yaxis_min}
            minY={yaxis_min}
            maxY="auto"
            yScale={{
              type: "linear",
              min: "auto",
              max: "auto",
              stacked: true,
            }}
            axisBottom={{
              format: function (val) {
                if (xaxis_ticks.includes(val)) {
                  return val.substring(11, 16);
                } else {
                  return "";
                }
              },
            }}
            axisLeft={{
              format: function (val) {
                return FormatThousand(val);
              },
            }}
            colors={["#2789f5"]}
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default LineChart;
