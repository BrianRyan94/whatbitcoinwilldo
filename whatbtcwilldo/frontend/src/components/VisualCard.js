import React from "react";
import Box from "@material-ui/core/Box";
import { ResponsiveLine } from "@nivo/line";
import { ResponsiveBar } from "@nivo/bar";
import SharedStyles from "./SharedStyles";
import Card from "@material-ui/core/Card";
import InfoCard from "./InfoCard";
import CardContent from "@material-ui/core/CardContent";
import Typography from "@material-ui/core/Typography";
import { FormatThousand } from "./Util";
import { BsSquareFill } from "react-icons/bs";
import { useMediaQuery } from "react-responsive";

const yTickFormatter = (val, title) => {
  if (title.substring(0, 5) == "Price") {
    return FormatThousand(val);
  }

  if (title.substring(0, 6) == "Volume") {
    return parseInt(val * 100) + "%";
  }

  if (title.substring(0, 10) == "Volatility") {
    return Math.round(val * 100, 2) + "%";
  }

  if (title.substring(0, 24) == "Average Trade Size (BTC)") {
    return val;
  }
};

const customLegend = (text, color, shared_style) => {
  return (
    <div className={shared_style.legend}>
      <div className={shared_style.legend_text} fontSize={5}>
        {text}
      </div>
      <BsSquareFill className={shared_style.legend_icon} color={color} />
    </div>
  );
};

const chartTheme = {
  fontFamily: "Quicksand",
  tooltip: {
    fontFamily: "Quicksand",
    fontSize: "10px",
    container: {
      background: "white",
    },
  },
};

const ChartElement = (
  chart_type,
  data,
  shared_style,
  yaxis_min,
  title,
  xaxis_ticks,
  yaxis_label,
  colorControl,
  tick_rotation
) => {
  if (data == null || data.length == 0) {
    return null;
  }

  const x_values = data[0].data.map((val) => val.x);
  if (chart_type == "line") {
    return (
      <div className={shared_style.default_chart_dim}>
        <ResponsiveLine
          data={data}
          margin={{
            top: 10,
            right: 30,
            bottom: tick_rotation == "0" ? 50 : 60,
            left: 60,
          }}
          useMesh={true}
          debugMesh={false}
          theme={chartTheme}
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
              return xaxis_ticks[val] ? xaxis_ticks[val] : "";
            },
            tickRotation: tick_rotation,
            tickValues: Object.keys(xaxis_ticks).filter((val) =>
              x_values.includes(val)
            ),
          }}
          axisLeft={{
            format: (val) => yTickFormatter(val, title),
            legend: yaxis_label,
            legendPosition: "middle",
            legendOffset: -55,
            tickValues: 3,
          }}
          colors={["#2789f5"]}
          tooltip={(value) => {
            return (
              <Box boxShadow={1} className={shared_style.hover_container}>
                {yTickFormatter(value.point.data.y, title)}
              </Box>
            );
          }}
        />
      </div>
    );
  }

  if (chart_type == "bar") {
    let color_min = colorControl[0];
    let color_neutral = colorControl[1];
    let color_max = colorControl[2];
    return (
      <div className={shared_style.default_chart_dim}>
        <div className={shared_style.flexRow}>
          {customLegend(
            `>Normal ${
              title.substring(0, 6) == "Volume" ? "Volume" : "Avg. Trade Size"
            }`,
            "rgba(0, 230, 113)",
            shared_style
          )}
          {customLegend(
            `<Normal ${
              title.substring(0, 6) == "Volume" ? "Volume" : "Avg. Trade Size"
            }`,
            "rgba(255, 0, 0)",
            shared_style
          )}
        </div>
        <ResponsiveBar
          data={data[0].data}
          indexBy="x"
          theme={chartTheme}
          tooltip={(value) => {
            let y_val = yTickFormatter(value.data.y, title);
            return `${y_val}`;
          }}
          keys={["y"]}
          margin={{
            top: 10,
            right: 30,
            bottom: tick_rotation == "0" ? 50 : 60,
            left: 60,
          }}
          padding={0.3}
          valueScale={{ type: "linear" }}
          colors={(val) => {
            const bar_value = val.value;
            let alpha;
            let color;

            if (bar_value >= color_neutral) {
              alpha = (bar_value - color_neutral) / (color_max - color_neutral);
              alpha = Math.max(0.3, alpha);
              color = `rgba(0, 230, 113, ${alpha})`;
            } else {
              alpha = (color_neutral - bar_value) / (color_neutral - color_min);
              alpha = Math.max(0.3, alpha);
              color = `rgba(255, 0, 0, ${alpha})`;
            }

            return color;
          }}
          borderColor={{ from: "color", modifiers: [["darker", 1.6]] }}
          axisTop={null}
          axisRight={null}
          axisBottom={{
            format: function (val) {
              return xaxis_ticks[val] ? xaxis_ticks[val] : "";
            },
            tickRotation: tick_rotation,
            tickValues: Object.keys(xaxis_ticks).filter((val) =>
              x_values.includes(val)
            ),
          }}
          axisLeft={{
            format: (val) => yTickFormatter(val, title),

            tickValues: 5,
          }}
          enableLabel={false}
          animate={true}
          motionStiffness={90}
          motionDamping={15}
        />
      </div>
    );
  }
};

const VisualCard = ({
  dataseries,
  title,
  error,
  infoArray,
  target_column,
  data_transform,
  chart_type,
  colorControl,
  xticks,
}) => {
  var data;
  var yaxis_min;
  var yaxis_label;

  if (dataseries == null) {
    data = [];
  } else {
    dataseries = dataseries.map((row) => {
      return { x: row.dt, y: data_transform(row[target_column]) };
    });

    /*put data in format which can be processed by Nivo*/
    data = [{ id: "series", data: dataseries }];

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

  //if it is a narrow screen
  const narrow_screen = useMediaQuery({ maxWidth: 700 });
  //if it is big enough to have 2 on each row
  const row_display = useMediaQuery({ minWidth: 1000 });
  //if it is an extra wide screen
  const wide_screen = useMediaQuery({ minWidth: 1300 });

  //rotate tick values if either very narrow screen or else 2 per row and not wide screen
  let tick_rotation =
    (narrow_screen | row_display) & (wide_screen == false) ? -45 : 0;

  if (Object.values(xticks).length > 0) {
    if (Object.values(xticks)[0].length > 10) {
      tick_rotation = "-45";
    }
  }

  return (
    <Card variant="outlined" className={shared_style.visualCard}>
      <CardContent>
        <Typography className={shared_style.cardHeaders}>{title}</Typography>
        <InfoCard infoArray={infoArray} />
        {ChartElement(
          chart_type,
          data,
          shared_style,
          yaxis_min,
          title,
          xticks,
          yaxis_label,
          colorControl,
          tick_rotation
        )}
      </CardContent>
    </Card>
  );
};

export default VisualCard;
