import axios from "axios";

const getPriceList = async (endtime, hoursoffset) => {
  const params = { endtime, hoursoffset };

  const response = await axios.get("/api/rawprices", { params });

  if (response.status == 200) {
    return { data: response.data };
  } else {
    return { error: "Error occurred retrieving data." };
  }
};

const getVolumeList = async (endtime, hoursoffset) => {
  const params = { endtime, hoursoffset };

  const response = await axios.get("/api/volumes", { params });

  if (response.status == 200) {
    return { data: response.data };
  } else {
    return { error: "Error occurred retrieving data" };
  }
};

const getVolatilityList = async (endtime, hoursoffset) => {
  const params = { endtime, hoursoffset };

  const response = await axios.get("/api/volatilities", { params });

  if (response.status == 200) {
    return { data: response.data };
  } else {
    return { error: "Error occurred retrieving data" };
  }
};

const getAvgTradeList = async (endtime, hoursoffset) => {
  const params = { endtime, hoursoffset };
  const response = await axios.get("/api/avgtradesizes", { params });

  if (response.status == 200) {
    return { data: response.data };
  } else {
    return { error: "Error occurred retrieving data" };
  }
};

const getReturnInfo = async () => {
  const response = await axios.get("/api/returninfo");
  if (response.status == 200) {
    return { data: response.data };
  } else {
    return { error: "Error occurred retrieving data" };
  }
};

export {
  getPriceList,
  getReturnInfo,
  getVolumeList,
  getVolatilityList,
  getAvgTradeList,
};
