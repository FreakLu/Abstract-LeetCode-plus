import React, { useEffect, useState } from "react";
import { getReviewItems } from "../services/api";
import "./ReviewGallery.css";

const ReviewGallery = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loadReviewItems = async () => {
            try {
                setItems(await getReviewItems());
            } catch (requestError) {
                setError(requestError.message);
            } finally {
                setLoading(false);
            }
        };

        loadReviewItems();
    }, []);

    if (loading) {
        return <div className="review-gallery-message">正在加载复习卡片...</div>;
    }

    if (error) {
        return <div className="review-gallery-message error">{error}</div>;
    }

    return (
        <section className="review-gallery">
            <div className="review-gallery-header">
                <h2>复习卡片</h2>
                <span>{items.length} 道题目</span>
            </div>

            {items.length === 0 ? (
                <div className="review-gallery-message">还没有保存复习记录。</div>
            ) : (
                <div className="review-card-grid">
                    {items.map((item) => (
                        <article
                            key={item.problem_number}
                            className={`review-card mastery-level-${item.mastery_level || 0}`}
                        >
                            <span className="review-card-number">
                                LeetCode {item.problem_number}
                            </span>
                            <h3>{item.problem_title}</h3>
                        </article>
                    ))}
                </div>
            )}
        </section>
    );
};

export default ReviewGallery;
