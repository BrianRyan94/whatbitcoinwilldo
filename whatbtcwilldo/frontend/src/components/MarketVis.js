import React, { useEffect, useState } from "react";
import VisualCard from "./VisualCard";
import { FormatThousand } from "./Util";
import { getPriceList, getReturnInfo } from "../../api/MarketDataQueries";

const MarketVis = () => {
  var endtime = "Now";
  var hoursoffset = 1;
  /*The end time and the hours offset determine what data is loaded - if they change then this component should rerender*/
  const [visualData, setVisualData] = useState({
    priceSeries: null,
    priceSeriesError: null,
    returnsInfoArray: null,
    returnsInfoError: null,
    lastPrice: null,
  });

  const UpdateVisualData = async () => {
    const priceResult = await getPriceList(endtime, hoursoffset);
    const ReturnsInfo = await getReturnInfo();

    let last_price = Math.floor(
      priceResult.data[priceResult.data.length - 1].trade
    );

    last_price = last_price ? `$${last_price}` : null;

    setVisualData({
      ...visualData,
      priceSeries: priceResult.data,
      priceSeriesError: priceResult.error,
      returnsInfoArray: ReturnsInfo.data,
      returnsInfoError: ReturnsInfo.error,
      lastPrice: last_price,
    });
  };

  /*the useEffect hook ensures that 1) the visualisation data is loaded when the
  page first renders and 2) if the end time or hours offset changes the visualisation data is updated*/

  useEffect(() => {
    UpdateVisualData();
  }, [endtime, hoursoffset]);

  return (
    <>
      <VisualCard
        dataseries={visualData.priceSeries}
        title={`Price ${
          visualData.lastPrice ? FormatThousand(visualData.lastPrice) : ""
        }`}
        error={visualData.priceSeriesError}
        infoArray={visualData.returnsInfoArray}
      />
    </>
  );
};

export default MarketVis;
