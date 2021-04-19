const FormatThousand = (num) => {
  return num.toString().replace(/(\d)(?=(\d{3})+(?!\d))/g, "$1,");
};

const tick_formatter = (lookback) => {
  const months = {
    "01": "Jan",
    "02": "Feb",
    "03": "Mar",
    "04": "Apr",
    "05": "May",
    "06": "Jun",
    "07": "Jul",
    "08": "Aug",
    "09": "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
  };
  if (lookback == 1) {
    return (x) => x.substring(11, 16);
  }

  if (lookback == 24) {
    return (x) => x.substring(11, 16);
  }

  if (lookback == 168) {
    return (x) => {
      let month = x.substring(5, 7);
      let date = x.substring(8, 10);
      let time = x.substring(11, 16);
      return date.concat("/").concat(month).concat("\n").concat(time);
    };
  }

  if (lookback == 720) {
    return (x) => {
      let month = months[x.substring(5, 7)];
      let date = x.substring(8, 10);
      return date.concat("-").concat(month);
    };
  }
};

const MakeXTicks = (arr, lookback) => {
  const desired_length = 10;
  const decrement = Math.floor(arr.length / desired_length);
  let xticks = {};

  let pointer = arr.length - 1;

  while (pointer > 0) {
    xticks[arr[pointer]] = tick_formatter(lookback)(arr[pointer]);
    pointer -= decrement;
  }

  return xticks;
};

const TimestampToString = (x) => {
  return x.substring(0, 10).concat(" ").concat(x.substring(11, 19));
};

export { FormatThousand, MakeXTicks, TimestampToString };
