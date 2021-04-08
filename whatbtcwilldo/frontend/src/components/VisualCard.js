import React from "react";
import { ResponsiveLine } from "@nivo/line";
import SharedStyles from "./SharedStyles";
import Card from "@material-ui/core/Card";
import InfoCard from "./InfoCard";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import { FormatThousand } from "./Util";

const VisualCard = ({ dataseries, title, error, infoArray }) => {
  var data;
  var xaxis_ticks;
  var xaxis_tick_count = 10;
  var yaxis_min;
  var yaxis_label;

  if (dataseries == null) {
    data = [];
  } else {
    dataseries = dataseries.map((row) => {
      return { x: row.dt, y: parseInt(row.trade) };
    });

    /*put data in format which can be processed by Nivo*/
    data = [{ id: "priceseries", data: dataseries }];
    /*add a tick to the x axis for every tick_increment'th element*/
    let tick_increment = Math.floor(dataseries.length / xaxis_tick_count);
    xaxis_ticks = [];
    for (var i = 0; i < dataseries.length; i += tick_increment) {
      xaxis_ticks.push(dataseries[i].x);
    }

    //get array of y axis values
    let yaxisvalues = dataseries.map((value) => {
      return value.y;
    });

    yaxis_min = Math.min(...yaxisvalues);
  }

  if (title == "Price") {
    yaxis_label = "Price ($)";
  }
  const shared_style = SharedStyles();

  return (
    <Card variant="outlined">
      <CardContent>
        <Typography className={shared_style.cardHeaders}>{title}</Typography>
        <InfoCard infoArray={infoArray} />
        <div className={shared_style.default_chart_dim}>
          <ResponsiveLine
            data={data}
            margin={{
              top: 50,
              right: 10,
              bottom: 50,
              left: 60,
            }}
            pointSize={1}
            pointBorderWidth={1}
            pointBorderColor={{ from: "serieColor" }}
            enableArea={true}
            areaBaselineValue={yaxis_min}
            minY={yaxis_min}
            maxY="auto"
            enableGridX={false}
            yScale={{
              type: "linear",
              min: "auto",
              max: "auto",
              stacked: true,
            }}
            axisBottom={{
              format: function (val) {
                return val.substring(11, 16);
              },
              tickRotation: window.innerWidth < 700 ? "-90" : "0",
              tickValues: xaxis_ticks,
            }}
            axisLeft={{
              format: function (val) {
                return FormatThousand(val);
              },

              legend: yaxis_label,
              legendPosition: "middle",
              legendOffset: -55,
              tickValues: 5,
            }}
            colors={["#2789f5"]}
          />
        </div>
      </CardContent>
    </Card>
  );
};

export default VisualCard;
