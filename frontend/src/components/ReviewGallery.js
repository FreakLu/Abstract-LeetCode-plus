import React, { useEffect, useState } from "react";
import { getReviewItems } from "../services/api";
import "./ReviewGallery.css";

const ReviewGallery = ({ onClose }) => {
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

    return (
        <section className="review-gallery">
            <button type="button" className="review-gallery-close" onClick={onClose}>
                <span aria-hidden="true">←</span>
                返回主页
            </button>

            <div className="review-gallery-header">
                <div className="review-gallery-title">
                    <h2>复习卡片</h2>
                    <p>Review Gallery</p>
                </div>
                <span className="review-gallery-count">共 {items.length} 道题目</span>
            </div>

            {loading ? (
                <div className="review-gallery-message">正在加载复习卡片...</div>
            ) : error ? (
                <div className="review-gallery-message error">{error}</div>
            ) : items.length === 0 ? (
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
