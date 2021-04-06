import React, { useEffect, useState } from "react";
import LineChart from "./LineChart";
import { getPriceList } from "../../api/MarketDataQueries";

const MarketVis = () => {
  var endtime = "Now";
  var hoursoffset = 1;
  /*The end time and the hours offset determine what data is loaded - if they change then this component should rerender*/
  const [visualData, setVisualData] = useState({
    priceSeries: null,
    priceSeriesError: null,
  });

  const UpdateVisualData = async () => {
    const priceResult = await getPriceList(endtime, hoursoffset);

    setVisualData({
      ...visualData,
      priceSeries: priceResult.data,
      priceSeriesError: priceResult.error,
    });
  };

  /*the useEffect hook ensures that 1) the visualisation data is loaded when the
  page first renders and 2) if the end time or hours offset changes the visualisation data is updated*/

  useEffect(() => {
    UpdateVisualData();
  }, [endtime, hoursoffset]);

  return (
    <>
      <LineChart
        dataseries={visualData.priceSeries}
        title="Price"
        error={visualData.priceSeriesError}
      />
    </>
  );
};

export default MarketVis;
