import React, { useEffect, useState } from "react";
import {
    getReviewActivity,
    getStudyPlan,
    getStudyPlanStrategies,
    saveStudyPlan,
} from "../services/api";
import "./StudyOverview.css";

const formatDateKey = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    return `${year}-${month}-${day}`;
};

const getActivityLevel = (total = 0) => {
    if (total >= 6) return 4;
    if (total >= 4) return 3;
    if (total >= 2) return 2;
    if (total >= 1) return 1;
    return 0;
};

const MONTH_LABELS = [
    "JAN", "FEB", "MAR", "APR", "MAY", "JUN",
    "JUL", "AUG", "SEP", "OCT", "NOV", "DEC",
];

const parseTargetDate = (targetDate) => {
    const [year, month, day] = (targetDate || "").split("-").map(Number);
    const now = new Date();

    return {
        year: year || now.getFullYear(),
        month: month || now.getMonth() + 1,
        day: day || now.getDate(),
    };
};

const getDaysInMonth = (year, month) => (
    new Date(year, month, 0).getDate()
);

const createMonthDays = (year = new Date().getFullYear(), month = new Date().getMonth()) => {
    const firstDay = new Date(year, month, 1);
    const days = [];
    const calendarStart = new Date(year, month, 1 - firstDay.getDay());

    for (let dayOffset = 0; dayOffset < 42; dayOffset += 1) {
        const calendarDate = new Date(calendarStart);
        calendarDate.setDate(calendarStart.getDate() + dayOffset);
        days.push(calendarDate);
    }

    return days;
};

const ActivityCell = ({ date, activity, compact = false, currentMonth = null }) => {
    const dateKey = formatDateKey(date);
    const dayActivity = activity[dateKey] || {};
    const total = dayActivity.total || 0;
    const isOutsideMonth = (
        currentMonth !== null && date.getMonth() !== currentMonth
    );

    return (
        <span
            className={`activity-cell level-${getActivityLevel(total)} ${
                compact ? "compact" : ""
            } ${isOutsideMonth ? "outside-month" : ""}`}
            title={isOutsideMonth ? undefined : `${dateKey}：学习 ${total} 次`}
        >
            {!compact && (
                <>
                    <span className="activity-day-number">{date.getDate()}</span>
                    {!isOutsideMonth && (
                        <span className="activity-day-detail">
                            <span>S {dayActivity.solve || 0}</span>
                            <span>R {dayActivity.review || 0}</span>
                        </span>
                    )}
                </>
            )}
        </span>
    );
};

const StudyOverview = () => {
    const [activity, setActivity] = useState({});
    const [strategies, setStrategies] = useState([]);
    const [plan, setPlan] = useState(null);
    const [viewMode, setViewMode] = useState("month");
    const [targetDate, setTargetDate] = useState("");
    const [strategy, setStrategy] = useState("classic");
    const [isPlanOpen, setIsPlanOpen] = useState(false);
    const [recommendedProblem, setRecommendedProblem] = useState("");
    const [error, setError] = useState("");

    useEffect(() => {
        setRecommendedProblem(plan?.remaining_problem_numbers?.[0] || "");
    }, [plan]);

    useEffect(() => {
        const loadOverview = async () => {
            try {
                const [activityData, strategyData, planData] = await Promise.all([
                    getReviewActivity(),
                    getStudyPlanStrategies(),
                    getStudyPlan(),
                ]);
                setActivity(activityData);
                setStrategies(strategyData);
                setPlan(planData);
                if (planData) {
                    setTargetDate(planData.target_date);
                    setStrategy(planData.strategy);
                } else {
                    setTargetDate(formatDateKey(new Date()));
                    setIsPlanOpen(true);
                }
            } catch (requestError) {
                setError(requestError.message);
            }
        };

        loadOverview();
    }, []);

    const handleSavePlan = async (event) => {
        event.preventDefault();

        try {
            const savedPlan = await saveStudyPlan(targetDate, strategy);
            setPlan(savedPlan);
            setIsPlanOpen(false);
            setError("");
        } catch (requestError) {
            setError(requestError.message);
        }
    };

    const recommendSequentialProblem = () => {
        setRecommendedProblem(plan?.remaining_problem_numbers?.[0] || "");
    };

    const recommendRandomProblem = () => {
        const remainingProblems = plan?.remaining_problem_numbers || [];
        if (!remainingProblems.length) {
            setRecommendedProblem("");
            return;
        }

        const randomIndex = Math.floor(Math.random() * remainingProblems.length);
        setRecommendedProblem(remainingProblems[randomIndex]);
    };

    const updateTargetDatePart = (part, value) => {
        const current = parseTargetDate(targetDate);
        const next = { ...current, [part]: Number(value) };
        next.day = Math.min(next.day, getDaysInMonth(next.year, next.month));
        setTargetDate(
            `${next.year}-${String(next.month).padStart(2, "0")}-${String(next.day).padStart(2, "0")}`
        );
    };

    const renderPlanForm = () => {
        const parsedTargetDate = parseTargetDate(targetDate);
        const currentYear = new Date().getFullYear();
        const selectableYears = Array.from({ length: 11 }, (_, index) => currentYear + index);
        const selectableDays = Array.from(
            { length: getDaysInMonth(parsedTargetDate.year, parsedTargetDate.month) },
            (_, index) => index + 1
        );

        return (
            <form className="study-plan-form" onSubmit={handleSavePlan}>
                <div>
                    <span className="study-overview-eyebrow">Study Plan</span>
                    <h3>{plan ? "调整学习计划" : "设置你的学习计划"}</h3>
                </div>
                <label>
                    目标日期
                    <div className="study-plan-date-selects">
                        <select
                            value={parsedTargetDate.year}
                            onChange={(event) => updateTargetDatePart("year", event.target.value)}
                        >
                            {selectableYears.map((year) => (
                                <option key={year} value={year}>{year} 年</option>
                            ))}
                        </select>
                        <select
                            value={parsedTargetDate.month}
                            onChange={(event) => updateTargetDatePart("month", event.target.value)}
                        >
                            {MONTH_LABELS.map((monthLabel, index) => (
                                <option key={monthLabel} value={index + 1}>{index + 1} 月</option>
                            ))}
                        </select>
                        <select
                            value={parsedTargetDate.day}
                            onChange={(event) => updateTargetDatePart("day", event.target.value)}
                        >
                            {selectableDays.map((day) => (
                                <option key={day} value={day}>{day} 日</option>
                            ))}
                        </select>
                    </div>
                </label>
                <label>
                    学习策略
                    <select
                        value={strategy}
                        onChange={(event) => setStrategy(event.target.value)}
                    >
                        {strategies.map((item) => (
                            <option key={item.id} value={item.id}>
                                {item.name}
                            </option>
                        ))}
                    </select>
                </label>
                <button type="submit">{plan ? "更新计划" : "开始计划"}</button>
            </form>
        );
    };

    const monthDays = createMonthDays();
    const currentYear = new Date().getFullYear();
    const currentMonth = new Date().getMonth();
    const currentMonthPrefix = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}`;
    const currentMonthActivity = Object.entries(activity)
        .filter(([activityDate]) => activityDate.startsWith(currentMonthPrefix))
        .reduce(
            (summary, [, counts]) => ({
                solve: summary.solve + (counts.solve || 0),
                review: summary.review + (counts.review || 0),
                total: summary.total + (counts.total || 0),
            }),
            { solve: 0, review: 0, total: 0 }
        );
    const todayActivity = activity[formatDateKey(new Date())] || {
        solve: 0,
        review: 0,
    };

    return (
        <section className="study-overview">
            {!plan ? (
                <div className="study-plan-onboarding">
                    {renderPlanForm()}
                </div>
            ) : (
                <div className="study-plan-control">
                    <button
                        type="button"
                        className="study-plan-trigger has-plan"
                        onClick={() => setIsPlanOpen((isOpen) => !isOpen)}
                    >
                        <span className="study-plan-trigger-icon">◎</span>
                        <span>
                            Today · Solve {todayActivity.solve || 0} · Review {todayActivity.review || 0}
                        </span>
                    </button>

                    {isPlanOpen && (
                        <div className="study-plan-popover">
                            <div className="study-plan-brief">
                                <span>{plan.strategy_name}</span>
                                <strong>{plan.completed_problems} / {plan.total_problems}</strong>
                                <p>剩余 {plan.remaining_days} 天，每日目标 {plan.daily_target} 题</p>
                            </div>
                            {renderPlanForm()}
                        </div>
                    )}
                    {!isPlanOpen && (
                        <>
                            <div className="study-plan-status">
                                <span>当前计划：{plan.strategy_name}</span>
                                <strong>{plan.completed_problems} / {plan.total_problems}</strong>
                                <p>剩余 {plan.remaining_days} 天，每日目标 {plan.daily_target} 题</p>
                            </div>
                            <div className="next-problem-recommendation">
                                <span>下一题推荐</span>
                                <strong>
                                    {recommendedProblem
                                        ? `#${recommendedProblem}`
                                        : "计划已完成"}
                                </strong>
                                <div className="next-problem-actions">
                                    <button
                                        type="button"
                                        className="recommendation-action"
                                        data-tooltip="随机"
                                        aria-label="随机推荐题目"
                                        onClick={recommendRandomProblem}
                                    >
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path d="M4 7h3.5c4 0 5 10 9 10H20" />
                                            <path d="m17 14 3 3-3 3" />
                                            <path d="M4 17h3.5c1.4 0 2.5-1.2 3.5-2.8" />
                                            <path d="M13 9.8C14 8.2 15 7 16.5 7H20" />
                                            <path d="m17 4 3 3-3 3" />
                                        </svg>
                                    </button>
                                    <button
                                        type="button"
                                        className="recommendation-action"
                                        data-tooltip="顺序"
                                        aria-label="按顺序推荐题目"
                                        onClick={recommendSequentialProblem}
                                    >
                                        <svg viewBox="0 0 24 24" aria-hidden="true">
                                            <path d="M5 6h11" />
                                            <path d="M5 12h11" />
                                            <path d="M5 18h11" />
                                            <path d="m16 15 3 3-3 3" />
                                        </svg>
                                    </button>
                                </div>
                            </div>
                        </>
                    )}
                </div>
            )}

            <div className="activity-panel">
                <div className="activity-header">
                    <div className="activity-heading">
                        <div className="activity-heading-top">
                            <span className="study-overview-eyebrow">Learning Activity</span>
                            <div className="activity-view-switch">
                                <button
                                    type="button"
                                    className={viewMode === "month" ? "active" : ""}
                                    onClick={() => setViewMode("month")}
                                >
                                    MONTH
                                </button>
                                <button
                                    type="button"
                                    className={viewMode === "year" ? "active" : ""}
                                    onClick={() => setViewMode("year")}
                                >
                                    YEAR
                                </button>
                            </div>
                        </div>
                        <h3>
                            {viewMode === "month"
                                ? `${MONTH_LABELS[currentMonth]} ${currentYear}`
                                : `${currentYear} 学习活跃度`}
                        </h3>
                        {viewMode === "month" && (
                            <p className="activity-month-summary">
                                Solve {currentMonthActivity.solve}
                                <span>·</span>
                                Review {currentMonthActivity.review}
                                <span>·</span>
                                Total {currentMonthActivity.total}
                            </p>
                        )}
                    </div>
                </div>

                {viewMode === "month" ? (
                    <div className="activity-month-grid">
                        {monthDays.map((date) => (
                            <ActivityCell
                                key={formatDateKey(date)}
                                date={date}
                                activity={activity}
                                currentMonth={currentMonth}
                            />
                        ))}
                    </div>
                ) : (
                    <div className="activity-year-months">
                        {MONTH_LABELS.map((monthLabel, monthIndex) => (
                            <div className="activity-year-month" key={monthLabel}>
                                <span>{monthLabel}</span>
                                <div>
                                    {createMonthDays(currentYear, monthIndex)
                                        .filter((date) => date.getMonth() === monthIndex)
                                        .map((date) => (
                                            <ActivityCell
                                                key={formatDateKey(date)}
                                                date={date}
                                                activity={activity}
                                                compact
                                            />
                                        ))}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {error && <p className="study-overview-error">{error}</p>}
        </section>
    );
};

export default StudyOverview;
