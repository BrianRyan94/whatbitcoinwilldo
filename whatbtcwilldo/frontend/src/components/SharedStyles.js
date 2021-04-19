import { makeStyles } from "@material-ui/core/styles";

const SharedStyles = makeStyles({
  primary_background: {
    background: "#2789f5",
    padding: "15px",
  },

  primary_color: {
    color: "#2789f5",
  },

  secondary_background: {
    backgroundColor: "rgba(20, 20, 20, 0.05)",
  },

  header_text: {
    color: "white",
  },

  cardHeaders: {
    color: "#2789f5",
    fontWeight: "bolder",
  },

  default_chart_dim: {
    width: "100%",
    height: "300px",
  },

  flexRow: {
    display: "flex",
    flexDirection: "row",
  },

  spaceBetween: {
    justifyContent: "space-between",
  },

  RowWrap: {
    flexFlow: "row wrap",
  },

  legend: {
    display: "flex",
    flexDirection: "row",
    marginRight: "10px",
    justifyContent: "space_between",
    marginTop: "10px",
  },

  legend_icon: {
    marginLeft: "10px",
    fontSize: "14px",
  },

  legend_text: {
    fontSize: "12px",
    fontFamily: "Quicksand",
  },

  main_content: {
    marginTop: "20px",
  },

  LookbackSelection: {
    justifyContent: "center",
  },

  LookbackOption: {
    backgroundColor: "red",
    border: "1px solid black",
  },

  visualCard: {
    marginTop: "15px",
    marginLeft: "10px",
    marginRight: "10px",
    flex: 1,
  },

  centered_within: {
    display: "flex",
    flexDirection: "row",
    justifyContent: "center",
  },

  hover_container: {
    borderRadius: "3px",
    backgroundColor: "white",
    padding: "3px",
  },

  Footer: {
    width: "100%",
    margin: "auto",
    marginTop: "20px",
    height: "100px",
    textAlign: "center",
    display: "flex",
    height: "40px",
    flexDirection: "column",
    justifyContent: "center",
    color: "white",
  },
});

export default SharedStyles;
