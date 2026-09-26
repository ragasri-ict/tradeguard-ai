import { useEffect, useState } from "react";
import "./App.css";

import {
  getCompanies,
  getHealth,
  analyzeAttribution,
} from "./services/api";


function App() {

  // ==========================================
  // STATE
  // ==========================================

  const [companies, setCompanies] = useState([]);

  const [selectedSymbol, setSelectedSymbol] =
    useState("TCS");

  const [selectedDate, setSelectedDate] =
    useState("2025-01-17");

  const [data, setData] = useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");

  const [backendStatus, setBackendStatus] =
    useState("Checking...");


  // ==========================================
  // LOAD COMPANIES + CHECK BACKEND
  // ==========================================

  useEffect(() => {

    loadInitialData();

  }, []);


  async function loadInitialData() {

    try {

      const companyResult =
        await getCompanies();

      setCompanies(
        companyResult.companies || []
      );

    } catch (err) {

      setError(
        "Unable to load companies from backend."
      );

    }


    try {

      await getHealth();

      setBackendStatus(
        "Backend Connected"
      );

    } catch (err) {

      setBackendStatus(
        "Backend Offline"
      );

    }

  }


  // ==========================================
  // GET SELECTED COMPANY
  // ==========================================

  const selectedCompany =
    companies.find(
      (company) =>
        company.symbol === selectedSymbol
    );


  // ==========================================
  // ANALYZE EVENT
  // ==========================================

  async function handleAnalyze() {

    setLoading(true);
    setError("");

    try {

      const result =
        await analyzeAttribution(
          selectedSymbol,
          selectedDate
        );

      setData(result);

    } catch (err) {

      setData(null);

      setError(
        err.message ||
        "Unable to analyze event."
      );

    } finally {

      setLoading(false);

    }

  }


  // ==========================================
  // FORMATTING
  // ==========================================

  function formatPercent(value) {

    if (
      value === null ||
      value === undefined
    ) {

      return "-";

    }

    return (
      Number(value).toFixed(2) +
      "%"
    );

  }


  function formatNumber(value) {

    if (
      value === null ||
      value === undefined
    ) {

      return "-";

    }

    return Number(value).toFixed(2);

  }


  // ==========================================
  // RENDER
  // ==========================================

  return (

    <div className="dashboard">


      {/* =====================================
          SIDEBAR
      ====================================== */}

      <aside className="sidebar">

        <div className="logo">

          <div className="logo-icon">
            AI
          </div>

          <div>

            <h2>
              MarketIntel
            </h2>

            <span>
              Event Attribution
            </span>

          </div>

        </div>


        <nav>

          <button
            className="nav-item active"
            type="button"
          >
            📊 Dashboard
          </button>

          <button
            className="nav-item"
            type="button"
          >
            📈 Market Events
          </button>

          <button
            className="nav-item"
            type="button"
          >
            🔎 Event Analysis
          </button>

          <button
            className="nav-item"
            type="button"
          >
            📰 News Intelligence
          </button>

          <button
            className="nav-item"
            type="button"
          >
            📚 Historical Events
          </button>

          <button
            className="nav-item"
            type="button"
          >
            📄 Reports
          </button>

        </nav>


        <div className="sidebar-bottom">

          <div className="system-status">

            <span className="status-dot"></span>

            {backendStatus}

          </div>


          <small>
            FastAPI + Attribution Engine
          </small>

        </div>

      </aside>


      {/* =====================================
          MAIN CONTENT
      ====================================== */}

      <main className="main-content">


        {/* HEADER */}

        <header className="topbar">

          <div>

            <h1>
              Market Event Intelligence
            </h1>

            <p>
              AI-powered detection and attribution
              of abnormal market events
            </p>

          </div>


          <div className="header-actions">

            <button
              className="icon-button"
              type="button"
            >
              🔔
            </button>


            <div className="profile">

              <div className="avatar">
                LS
              </div>

              <div>

                <strong>
                  Analyst
                </strong>

                <span>
                  Market Research
                </span>

              </div>

            </div>

          </div>

        </header>


        {/* =====================================
            FILTER BAR
        ====================================== */}

        <section className="filter-bar">


          <div>

            <label>
              Stock
            </label>


            <select
              value={selectedSymbol}
              onChange={(e) =>
                setSelectedSymbol(
                  e.target.value
                )
              }
            >

              {companies.length === 0 ? (

                <option>
                  Loading...
                </option>

              ) : (

                companies.map(
                  (company) => (

                    <option
                      key={company.symbol}
                      value={company.symbol}
                    >
                      {company.company}
                    </option>

                  )
                )

              )}

            </select>

          </div>


          <div>

            <label>
              Sector
            </label>


            <select
              value={
                selectedCompany
                  ? selectedCompany.sector
                  : ""
              }
              disabled
            >

              <option>

                {selectedCompany
                  ? selectedCompany.sector
                  : "Loading..."}

              </option>

            </select>

          </div>


          <div>

            <label>
              Analysis Date
            </label>


            <input
              type="date"
              value={selectedDate}
              onChange={(e) =>
                setSelectedDate(
                  e.target.value
                )
              }
              style={{
                border:
                  "1px solid #dfe3eb",
                background:
                  "white",
                padding:
                  "9px 12px",
                borderRadius:
                  "8px",
                color:
                  "#273043",
              }}
            />

          </div>


          <button
            className="analyze-button"
            type="button"
            onClick={handleAnalyze}
            disabled={
              loading ||
              companies.length === 0
            }
          >

            {loading
              ? "Analyzing..."
              : "Analyze Event"}

          </button>

        </section>


        {/* =====================================
            ERROR
        ====================================== */}

        {error && (

          <section
            className="panel"
            style={{
              marginBottom:
                "20px",
              color:
                "#dc3545",
            }}
          >

            {error}

          </section>

        )}


        {/* =====================================
            LOADING
        ====================================== */}

        {loading && (

          <section
            className="panel"
            style={{
              marginBottom:
                "20px",
            }}
          >

            Analyzing stock,
            market, sector,
            events and historical
            evidence...

          </section>

        )}


        {/* =====================================
            RESULTS
        ====================================== */}

        {data && (

          <>

            {/* =================================
                MOVEMENT CARDS
            ================================== */}

            <section
              className="stats-grid"
            >


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    Stock Return
                  </span>

                  <span className="stat-icon">
                    📈
                  </span>

                </div>


                <h2>
                  {formatPercent(
                    data.movement
                      .stock_return
                  )}
                </h2>


                <p
                  className={
                    data.movement
                      .stock_return >= 0
                      ? "positive"
                      : "negative"
                  }
                >

                  {data.symbol}

                </p>

              </div>


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    Sector Return
                  </span>

                  <span className="stat-icon">
                    🏭
                  </span>

                </div>


                <h2>
                  {formatPercent(
                    data.movement
                      .sector_return
                  )}
                </h2>


                <p>
                  {data.sector}
                </p>

              </div>


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    NIFTY 50 Return
                  </span>

                  <span className="stat-icon">
                    📊
                  </span>

                </div>


                <h2>
                  {formatPercent(
                    data.movement
                      .nifty_return
                  )}
                </h2>


                <p>
                  Broader market
                </p>

              </div>


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    Market Divergence
                  </span>

                  <span className="stat-icon">
                    ↕
                  </span>

                </div>


                <h2>
                  {formatPercent(
                    data.movement
                      .market_divergence
                  )}
                </h2>


                <p>
                  Stock vs NIFTY
                </p>

              </div>

            </section>


            {/* =================================
                ATTRIBUTION
            ================================== */}

            <section
              className="content-grid"
            >


              <div className="panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Cause Attribution
                    </h2>

                    <p>
                      Rule-based evidence
                      analysis
                    </p>

                  </div>

                </div>


                <div className="event-list">


                  <div className="event-row">

                    <div className="event-name">
                      Company Event
                    </div>

                    <strong>
                      {formatPercent(
                        data.attribution
                          .company_event_score
                      )}
                    </strong>

                  </div>


                  <div className="event-row">

                    <div className="event-name">
                      Sector Movement
                    </div>

                    <strong>
                      {formatPercent(
                        data.attribution
                          .sector_movement_score
                      )}
                    </strong>

                  </div>


                  <div className="event-row">

                    <div className="event-name">
                      Market Movement
                    </div>

                    <strong>
                      {formatPercent(
                        data.attribution
                          .market_movement_score
                      )}
                    </strong>

                  </div>


                  <div className="event-row">

                    <div className="event-name">
                      Technical Flow
                    </div>

                    <strong>
                      {formatPercent(
                        data.attribution
                          .technical_flow_score
                      )}
                    </strong>

                  </div>


                  <div className="event-row">

                    <div className="event-name">
                      Stock-Specific Move
                    </div>

                    <strong>
                      {formatPercent(
                        data.attribution
                          .stock_specific_move_score
                      )}
                    </strong>

                  </div>

                </div>

              </div>


              <div className="panel">

                <div className="panel-header">

                  <div>

                    <h2>
                      Primary Attribution
                    </h2>

                    <p>
                      Highest rule-based
                      score
                    </p>

                  </div>

                </div>


                <h2
                  style={{
                    fontSize:
                      "24px",
                    marginBottom:
                      "12px",
                    wordBreak:
                      "break-word",
                  }}
                >
                  {
                    data.attribution
                      .primary_cause
                  }
                </h2>


                <p>
                  Attribution score
                </p>


                <h2>

                  {formatPercent(
                    data.attribution
                      .attribution_confidence
                  )}

                </h2>

              </div>

            </section>


            {/* =================================
                TECHNICAL
            ================================== */}

            <section
              className="stats-grid"
            >


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    Volume Ratio
                  </span>

                  <span>
                    📦
                  </span>

                </div>


                <h2>

                  {formatNumber(
                    data.technical
                      .volume_ratio
                  )}

                  x

                </h2>

              </div>


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    Volume Z-Score
                  </span>

                  <span>
                    📐
                  </span>

                </div>


                <h2>

                  {formatNumber(
                    data.technical
                      .volume_zscore
                  )}

                </h2>

              </div>


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    Company Event
                  </span>

                  <span>
                    📰
                  </span>

                </div>


                <h2>

                  {data.company_events
                    .present
                    ? "Found"
                    : "None"}

                </h2>

              </div>


              <div className="stat-card">

                <div className="stat-header">

                  <span>
                    Historical Match
                  </span>

                  <span>
                    📚
                  </span>

                </div>


                <h2>

                  {data.historical_matching
                    ?.historical_match_score
                    ?? "-"}

                </h2>

              </div>

            </section>


            {/* =================================
                COMPANY EVENT
            ================================== */}

            <section
              className="panel recent-events"
            >

              <div className="panel-header">

                <div>

                  <h2>
                    Company Event Evidence
                  </h2>

                  <p>
                    Events found on the
                    selected date
                  </p>

                </div>

              </div>


              {data.company_events
                .present ? (

                data.company_events
                  .events
                  .map(
                    (event, index) => (

                      <div
                        className="event-item"
                        key={index}
                      >

                        <strong>
                          {
                            event.event_type
                          }
                        </strong>

                        <br />

                        {
                          event.subject
                        }

                      </div>

                    )
                  )

              ) : (

                <p>
                  No company-specific
                  event found.
                </p>

              )}

            </section>


            {/* =================================
                EXPLANATION
            ================================== */}

            <section
              className="panel recent-events"
            >

              <div className="panel-header">

                <div>

                  <h2>
                    Explainable Analysis
                  </h2>

                  <p>
                    Evidence-based
                    interpretation
                  </p>

                </div>

              </div>


              <p
                style={{
                  lineHeight:
                    "1.8",
                  color:
                    "#4b5563",
                }}
              >
                {data.explanation}
              </p>

            </section>


            {/* =================================
                ALTERNATIVE EVIDENCE
            ================================== */}

            <section
              className="panel recent-events"
            >

              <div className="panel-header">

                <div>

                  <h2>
                    Alternative Evidence
                  </h2>

                  <p>
                    Other evidence that
                    may explain the movement
                  </p>

                </div>

              </div>


              {data.alternative_analysis
                ?.alternative_causes
                ?.length > 0 ? (

                data.alternative_analysis
                  .alternative_causes
                  .map(
                    (item, index) => (

                      <div
                        className="event-item"
                        key={index}
                      >

                        <strong>
                          {item.factor}
                        </strong>

                        <br />

                        {item.message}

                      </div>

                    )
                  )

              ) : (

                <p>
                  No strong alternative
                  explanation identified.
                </p>

              )}


              {data.alternative_analysis
                ?.contradictory_evidence
                ?.length > 0 && (

                <div
                  style={{
                    marginTop:
                      "15px",
                  }}
                >

                  <strong>
                    Contradictory Evidence
                  </strong>


                  {data.alternative_analysis
                    .contradictory_evidence
                    .map(
                      (item, index) => (

                        <div
                          className="event-item"
                          key={index}
                        >

                          <strong>
                            {item.factor}
                          </strong>

                          <br />

                          {item.message}

                        </div>

                      )
                    )}

                </div>

              )}

            </section>


            {/* =================================
                HISTORICAL MATCHING
            ================================== */}

            <section
              className="panel recent-events"
            >

              <div className="panel-header">

                <div>

                  <h2>
                    Historical Event Matching
                  </h2>

                  <p>
                    Similar previous
                    movement patterns
                  </p>

                </div>

              </div>


              <div
                className="table-container"
              >

                <table>

                  <tbody>


                    <tr>

                      <th>
                        Match Score
                      </th>

                      <td>
                        {
                          data.historical_matching
                            ?.historical_match_score
                          ?? "-"
                        }
                      </td>

                    </tr>


                    <tr>

                      <th>
                        Match Count
                      </th>

                      <td>
                        {
                          data.historical_matching
                            ?.historical_match_count
                          ?? "-"
                        }
                      </td>

                    </tr>


                    <tr>

                      <th>
                        Average Historical Return
                      </th>

                      <td>

                        {
                          data.historical_matching
                            ?.historical_avg_return
                          !== null &&
                          data.historical_matching
                            ?.historical_avg_return
                          !== undefined

                            ? formatPercent(
                                data.historical_matching
                                  .historical_avg_return
                              )

                            : "-"
                        }

                      </td>

                    </tr>


                    <tr>

                      <th>
                        Median Historical Return
                      </th>

                      <td>

                        {
                          data.historical_matching
                            ?.historical_median_return
                          !== null &&
                          data.historical_matching
                            ?.historical_median_return
                          !== undefined

                            ? formatPercent(
                                data.historical_matching
                                  .historical_median_return
                              )

                            : "-"
                        }

                      </td>

                    </tr>


                    <tr>

                      <th>
                        Expected Reaction
                      </th>

                      <td>
                        {
                          data.historical_matching
                            ?.expected_reaction
                          ?? "-"
                        }
                      </td>

                    </tr>


                    <tr>

                      <th>
                        Matching Dates
                      </th>

                      <td
                        style={{
                          wordBreak:
                            "break-word",
                        }}
                      >
                        {
                          data.historical_matching
                            ?.historical_match_dates
                          ?? "-"
                        }
                      </td>

                    </tr>


                  </tbody>

                </table>

              </div>

            </section>


            {/* =================================
                COUNTERFACTUAL
            ================================== */}

            <section
              className="panel recent-events"
            >

              <div className="panel-header">

                <div>

                  <h2>
                    Counterfactual
                    Evidence Sensitivity
                  </h2>

                  <p>
                    Attribution after
                    removing one
                    evidence factor
                  </p>

                </div>

              </div>


              <div
                className="table-container"
              >

                <table>

                  <thead>

                    <tr>

                      <th>
                        Removed Evidence
                      </th>

                      <th>
                        New Primary Cause
                      </th>

                      <th>
                        Score Change
                      </th>

                      <th>
                        Cause Changed
                      </th>

                    </tr>

                  </thead>


                  <tbody>

                    {data.counterfactual_analysis
                      ?.map(
                        (item, index) => (

                          <tr key={index}>

                            <td>
                              {
                                item.removed_factor
                              }
                            </td>

                            <td>
                              {
                                item.counterfactual_primary_cause
                              }
                            </td>

                            <td>
                              {
                                Number(
                                  item.score_change
                                ).toFixed(2)
                              }
                            </td>

                            <td>
                              {
                                item.primary_cause_changed
                                  ? "Yes"
                                  : "No"
                              }
                            </td>

                          </tr>

                        )
                      )}

                  </tbody>

                </table>

              </div>

            </section>

          </>

        )}


        {/* =====================================
            INITIAL STATE
        ====================================== */}

        {!data &&
          !loading &&
          !error && (

            <section
              className="panel"
            >

              <h2>
                Ready for analysis
              </h2>

              <p
                style={{
                  marginTop:
                    "10px",
                  color:
                    "#6b7280",
                }}
              >
                Select a stock and
                date, then click
                Analyze Event.
              </p>

            </section>

          )}


        {/* =====================================
            FOOTER
        ====================================== */}

        <footer>

          <span>
            AI Market Event Attribution System
          </span>

          <span>
            FastAPI • ML Detection • Historical
            Matching • Explainability
          </span>

        </footer>


      </main>

    </div>
  );
}


export default App;