import streamlit as st
import pandas as pd
import pymongo
from datetime import datetime
import plotly.express as px

# -------------------------
# MongoDB Connection
# -------------------------
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["expense_tracker"]
collection = db["expenses"]

st.set_page_config(page_title="Expense Tracker", layout="wide")

st.title("💰 Expense Tracker")

# -------------------------
# Sidebar Menu
# ------------------------
menu = ["Add Expense", "View Expenses", "Dashboard"]
choice = st.sidebar.selectbox("Menu", menu)

# -------------------------
# Add Expense
# -------------------------
if choice == "Add Expense":
    st.subheader("➕ Add a New Expense")
    
    with st.form("expense_form", clear_on_submit=True):
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Other"])
        amount = st.number_input("Amount (₹)", min_value=1)
        description = st.text_input("Description")
        date = st.date_input("Date", datetime.today())
        
        submitted = st.form_submit_button("Add Expense")
        
        if submitted:
            expense = {
                "category": category,
                "amount": amount,
                "description": description,
                "date": datetime.combine(date, datetime.min.time())
            }
            collection.insert_one(expense)
            st.success("✅ Expense Added Successfully!")

# -------------------------
# View Expenses
# -------------------------
elif choice == "View Expenses":
    st.subheader("📋 All Expenses")
    
    data = list(collection.find({}, {"_id": 0}))
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        # Filters
        with st.expander("🔍 Filters"):
            cat_filter = st.multiselect("Filter by Category", df["category"].unique())
            if cat_filter:
                df = df[df["category"].isin(cat_filter)]
            
            start_date = st.date_input("Start Date", min(df["date"]))
            end_date = st.date_input("End Date", max(df["date"]))
            df = df[(df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))]
        
        st.dataframe(df, use_container_width=True)

        # Delete option
        if st.button("🗑️ Delete All Expenses"):
            collection.delete_many({})
            st.warning("All expenses deleted!")
    else:
        st.info("No expenses found. Please add some.")

# -------------------------
# Dashboard
# -------------------------
elif choice == "Dashboard":
    st.subheader("📊 Expense Summary")
    
    data = list(collection.find({}, {"_id": 0}))
    if len(data) > 0:
        df = pd.DataFrame(data)
        
        total_spent = df["amount"].sum()
        st.metric("💵 Total Spent", f"₹ {total_spent}")
        
        # Category-wise chart
        cat_chart = px.bar(df.groupby("category")["amount"].sum().reset_index(),
                           x="category", y="amount", title="Category-wise Spending")
        st.plotly_chart(cat_chart, use_container_width=True)
        
        # Date-wise trend
        date_chart = px.line(df.groupby("date")["amount"].sum().reset_index(),
                             x="date", y="amount", title="Daily Spending Trend")
        st.plotly_chart(date_chart, use_container_width=True)
    else:
        st.info("No expenses found.")
