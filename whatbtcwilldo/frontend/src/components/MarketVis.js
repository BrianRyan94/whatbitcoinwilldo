import React, { useEffect, useState } from "react";
import VisualCard from "./VisualCard";
import ToggleButtons from "./ToggleButtons";
import { FormatThousand, MakeXTicks, TimestampToString } from "./Util";
import { Container } from "@material-ui/core";
import SharedStyles from "./SharedStyles";
import {
  getPriceList,
  getReturnInfo,
  getVolatilityList,
  getVolumeList,
  getAvgTradeList,
} from "../../api/MarketDataQueries";
import { useMediaQuery } from "react-responsive";

const hours_offset_options = {
  "1H": 1,
  "24H": 24,
  "1W": 168,
  "1M": 720,
};

const default_hours_offset = "24H";

const MarketVis = () => {
  var endtime = "Now";
  /*The end time and the hours offset determine what data is loaded - if they change then this component should rerender*/
  const [visualData, setVisualData] = useState({
    priceSeries: null,
    priceSeriesError: null,
    volumeSeries: null,
    volumeSeriesError: null,
    volatilitySeries: null,
    volatilitySeriesError: null,
    avgTradeSeries: null,
    avgTradeInfoArray: null,
    avgTradeSeriesError: null,
    historicalAvgTrdSize: null,
    returnsInfoArray: null,
    returnsInfoError: null,
    volatilityInfoArray: null,
    volumeInfoArray: null,
    lastPrice: null,
  });

  ///extract the time values from the price. Should be the same across each visual card
  const time_values = visualData.priceSeries
    ? visualData.priceSeries.map((obj) => obj.dt)
    : null;

  const xticks = time_values
    ? MakeXTicks(time_values, visualData.hoursoffset)
    : [];

  const UpdateVisualData = async (hours_offset_chosen) => {
    const hoursoffset = hours_offset_options[hours_offset_chosen];
    const priceResult = await getPriceList(endtime, hoursoffset);

    const avgTradeResult = await getAvgTradeList(endtime, hoursoffset);
    const volumeResult = await getVolumeList(endtime, hoursoffset);
    const volatilityResult = await getVolatilityList(endtime, hoursoffset);
    const ReturnsInfo = await getReturnInfo();

    let last_price = Math.floor(
      priceResult.data[priceResult.data.length - 1].trade
    );

    last_price = last_price ? `$${last_price}` : null;

    setVisualData({
      ...visualData,
      priceSeries: priceResult.data,
      priceSeriesError: priceResult.error,
      volumeSeries: volumeResult.data.chart_series,
      volumeSeriesError: volumeResult.error,
      volatilitySeries: volatilityResult.data.chart_series,
      volatilitySeriesError: volatilityResult.error,
      volumeInfoArray: volumeResult.data.info_array,
      volatilityInfoArray: volatilityResult.data.info_array,
      avgTradeSeries: avgTradeResult.data.chart_series,
      avgTradeInfoArray: avgTradeResult.data.info_array,
      avgTradeSeriesError: avgTradeResult.error,
      historicalAvgTrdSize: parseFloat(avgTradeResult.data.historical_average),
      returnsInfoArray: ReturnsInfo.data,
      returnsInfoError: ReturnsInfo.error,
      lastPrice: last_price,
      hoursoffset: hoursoffset,
    });
  };

  /*the useEffect hook ensures that the visualisation data is loaded when the page first renders*/

  useEffect(() => {
    //on page mount update the data with the default lookback (24 hours)
    UpdateVisualData(default_hours_offset);
  }, []);

  const shared_style = SharedStyles();
  const narrow_device = useMediaQuery({ query: "(max-width: 1000px)" });

  return (
    <Container maxWidth="50%" className={shared_style.main_content}>
      <ToggleButtons
        options={Object.keys(hours_offset_options)}
        defaultOption={default_hours_offset}
        callBack={UpdateVisualData}
      ></ToggleButtons>
      <div className={`${narrow_device ? null : shared_style.flexRow}`}>
        <VisualCard
          dataseries={visualData.priceSeries}
          title={`Price ${
            visualData.lastPrice ? FormatThousand(visualData.lastPrice) : ""
          }`}
          error={visualData.priceSeriesError}
          infoArray={visualData.returnsInfoArray}
          target_column="trade"
          data_transform={parseInt}
          chart_type="line"
          xticks={xticks}
        />

        <VisualCard
          dataseries={visualData.volatilitySeries}
          title={`Volatility`}
          error={visualData.volatilitySeriesError}
          infoArray={visualData.volatilityInfoArray}
          target_column="volatility"
          data_transform={parseFloat}
          chart_type="line"
          colorControl={[0, 1, 5]}
          xticks={xticks}
        />
      </div>

      <div className={`${narrow_device ? null : shared_style.flexRow}`}>
        <VisualCard
          dataseries={visualData.volumeSeries}
          title={`Volume Vs Normal`}
          error={visualData.volumeSeriesError}
          infoArray={visualData.volumeInfoArray}
          target_column="volume_vnorm"
          data_transform={parseFloat}
          chart_type="bar"
          colorControl={[0, 1, 5]}
          xticks={xticks}
        />

        <VisualCard
          dataseries={visualData.avgTradeSeries}
          title={"Average Trade Size (BTC)"}
          error={visualData.avgTradeSeriesError}
          infoArray={visualData.avgTradeInfoArray}
          target_column="avg_trade_size"
          data_transform={parseFloat}
          chart_type="bar"
          colorControl={[
            0,
            visualData.historicalAvgTrdSize,
            visualData.historicalAvgTrdSize + 0.1,
          ]}
          xticks={xticks}
        />
      </div>
    </Container>
  );
};

export default MarketVis;
