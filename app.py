import os
from datetime import date

import mysql.connector
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="RetailIQ | Sales & Profit Analytics",
    page_icon=":bar_chart:",
    layout="wide",
)

st.title("RetailIQ")
st.subheader("Retail Sales & Profit Analytics System")
st.caption("Track sales, understand profitability, and make better business decisions.")


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "retailiq_db"),
    )


def run_query(query, params=None, fetch=False):
    connection = get_connection()
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            return cursor.fetchall()
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def load_sales():
    query = """
        SELECT s.sale_id, s.sale_date, s.customer_name, s.product_id,
               p.product_name, p.category, s.quantity,
               s.unit_price, s.unit_cost,
               (s.quantity * s.unit_price) AS revenue,
               (s.quantity * s.unit_cost) AS total_cost,
               (s.quantity * (s.unit_price - s.unit_cost)) AS profit
        FROM sales s
        JOIN products p ON p.product_id = s.product_id
        ORDER BY s.sale_date DESC, s.sale_id DESC
    """
    df = pd.DataFrame(run_query(query, fetch=True))
    for col in ["unit_price", "unit_cost", "revenue", "total_cost", "profit"]:
        if col in df.columns:
            df[col] = df[col].astype(float)
    return df


def load_products():
    df = pd.DataFrame(run_query(
        """SELECT product_id, product_name, category, unit_price, unit_cost
           FROM products ORDER BY product_name""",
        fetch=True,
    ))
    for col in ["unit_price", "unit_cost"]:
        if col in df.columns:
            df[col] = df[col].astype(float)
    return df


def show_database_error(error):
    st.error("Could not connect to the RetailIQ database.")
    st.write(
        "Check that MySQL Server is running, that you ran schema.sql in "
        "MySQL Workbench, and that your connection settings are correct."
    )
    st.code(str(error))


page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Sale", "Manage Sales", "Products", "Business Insights"],
)
st.sidebar.divider()
st.sidebar.caption("Python · MySQL · SQL · Streamlit")

try:
    products = load_products()
    sales = load_sales()
except (mysql.connector.Error, KeyError, ValueError) as error:
    show_database_error(error)
    st.stop()

if page == "Dashboard":
    st.header("Sales & Profit Dashboard")

    if sales.empty:
        st.info(
            "No sales recorded yet. Add products on the Products "
            "page, then record a sale using Add Sale."
        )
    else:
        total_revenue = float(sales["revenue"].sum())
        total_profit = float(sales["profit"].sum())
        total_orders = int(len(sales))
        units_sold = int(sales["quantity"].sum())
        margin = (total_profit / total_revenue * 100) if total_revenue else 0

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Revenue", f"₹{total_revenue:,.2f}")
        c2.metric("Total Profit", f"₹{total_profit:,.2f}")
        c3.metric("Sales Records", f"{total_orders:,}")
        c4.metric("Units Sold", f"{units_sold:,}")
        c5.metric("Profit Margin", f"{margin:.1f}%")

        st.divider()

        left, right = st.columns(2)
        with left:
            st.subheader("Revenue by Product")
            by_product = sales.groupby("product_name")["revenue"].sum().sort_values(ascending=False)
            st.bar_chart(by_product)
        with right:
            st.subheader("Profit by Category")
            by_category = sales.groupby("category")["profit"].sum().sort_values(ascending=False)
            st.bar_chart(by_category)

        st.subheader("Monthly Revenue and Profit")
        monthly = sales.copy()
        monthly["sale_date"] = pd.to_datetime(monthly["sale_date"])
        monthly["month"] = monthly["sale_date"].dt.to_period("M").astype(str)
        monthly_summary = monthly.groupby("month")[["revenue", "profit"]].sum().sort_index()
        st.line_chart(monthly_summary)

        st.subheader("Recent Sales")
        st.dataframe(
            sales[["sale_id", "sale_date", "customer_name", "product_name",
                   "quantity", "revenue", "profit"]].head(10),
            use_container_width=True,
            hide_index=True,
        )

elif page == "Add Sale":
    st.header("Record a Sale")

    if products.empty:
        st.warning("Add at least one product on the Products page before recording a sale.")
    else:
        product_options = {
            f'{row["product_name"]} (ID {row["product_id"]})': row
            for _, row in products.iterrows()
        }

        with st.form("add_sale_form", clear_on_submit=True):
            selected_label = st.selectbox("Product", list(product_options.keys()))
            customer = st.text_input("Customer name (optional)")
            quantity = st.number_input("Quantity", min_value=1, max_value=100000, value=1, step=1)
            sale_date = st.date_input("Sale date", value=date.today())
            submitted = st.form_submit_button("Save Sale", type="primary")

        if submitted:
            selected = product_options[selected_label]
            try:
                run_query(
                    """INSERT INTO sales
                       (product_id, customer_name, quantity, unit_price, unit_cost, sale_date)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        int(selected["product_id"]),
                        customer.strip() or "Walk-in Customer",
                        int(quantity),
                        float(selected["unit_price"]),
                        float(selected["unit_cost"]),
                        sale_date,
                    ),
                )
                st.success("Sale recorded successfully!")
                st.rerun()
            except mysql.connector.Error as error:
                st.error(f"Could not save the sale: {error}")

elif page == "Manage Sales":
    st.header("Manage Sales Records")

    if sales.empty:
        st.info("There are no sales records to manage yet.")
    else:
        st.dataframe(sales, use_container_width=True, hide_index=True)
        st.caption("You can delete an incorrect record. A deleted record is permanently removed.")

        sale_ids = sales["sale_id"].astype(int).tolist()
        selected_id = st.selectbox("Choose a sale ID to delete", sale_ids)
        confirm = st.checkbox(f"I confirm that I want to delete sale ID {selected_id}")

        if st.button("Delete selected sale", disabled=not confirm):
            try:
                run_query("DELETE FROM sales WHERE sale_id = %s", (int(selected_id),))
                st.success(f"Sale ID {selected_id} deleted.")
                st.rerun()
            except mysql.connector.Error as error:
                st.error(f"Could not delete the sale: {error}")

elif page == "Products":
    st.header("Product Management")

    with st.expander("Add a new product", expanded=products.empty):
        with st.form("add_product_form", clear_on_submit=True):
            product_name = st.text_input("Product name")
            category = st.selectbox(
                "Category",
                ["Grocery", "Food & Beverage", "Personal Care", "Home",
                 "Electronics", "Clothing", "Other"],
            )
            unit_price = st.number_input("Selling price (₹)", min_value=0.01, value=100.00, step=10.00)
            unit_cost = st.number_input("Cost per unit (₹)", min_value=0.00, value=60.00, step=10.00)
            add_product = st.form_submit_button("Add Product", type="primary")

        if add_product:
            if not product_name.strip():
                st.warning("Enter a product name.")
            elif unit_cost > unit_price:
                st.warning("Cost is higher than selling price. Please check the values.")
            else:
                try:
                    run_query(
                        """INSERT INTO products (product_name, category, unit_price, unit_cost)
                           VALUES (%s, %s, %s, %s)""",
                        (product_name.strip(), category, float(unit_price), float(unit_cost)),
                    )
                    st.success("Product added successfully!")
                    st.rerun()
                except mysql.connector.Error as error:
                    st.error(f"Could not add product: {error}")

    st.subheader("Current Products")
    if products.empty:
        st.info("No products added yet.")
    else:
        st.dataframe(products, use_container_width=True, hide_index=True)

        st.subheader("Update a Product")
        product_map = {
            f'{row["product_name"]} (ID {row["product_id"]})': row
            for _, row in products.iterrows()
        }
        chosen = st.selectbox("Select product to update", list(product_map.keys()))
        item = product_map[chosen]

        with st.form("update_product_form"):
            new_name = st.text_input("Product name", value=str(item["product_name"]))
            new_category = st.text_input("Category", value=str(item["category"]))
            new_price = st.number_input(
                "Selling price (₹)",
                min_value=0.01,
                value=float(item["unit_price"]),
                step=10.00,
            )
            new_cost = st.number_input(
                "Cost per unit (₹)",
                min_value=0.00,
                value=float(item["unit_cost"]),
                step=10.00,
            )
            update_product = st.form_submit_button("Update Product")

        if update_product:
            if not new_name.strip():
                st.warning("Product name cannot be empty.")
            elif new_cost > new_price:
                st.warning("Cost is higher than selling price. Please check the values.")
            else:
                try:
                    run_query(
                        """UPDATE products SET product_name=%s, category=%s,
                           unit_price=%s, unit_cost=%s WHERE product_id=%s""",
                        (
                            new_name.strip(), new_category.strip() or "Other",
                            float(new_price), float(new_cost), int(item["product_id"]),
                        ),
                    )
                    st.success(
                        "Product updated. Existing sales retain the price "
                        "and cost recorded when they were created."
                    )
                    st.rerun()
                except mysql.connector.Error as error:
                    st.error(f"Could not update product: {error}")

elif page == "Business Insights":
    st.header("Business Insights & Recommendations")

    if sales.empty:
        st.info("Record some sales first. Business insights will appear here once data is available.")
    else:
        by_product = sales.groupby("product_name").agg(
            units_sold=("quantity", "sum"),
            revenue=("revenue", "sum"),
            profit=("profit", "sum"),
        ).sort_values("profit", ascending=False)

        best_product = by_product["profit"].idxmax()
        weakest_product = by_product["profit"].idxmin()
        best_category = sales.groupby("category")["profit"].sum().idxmax()
        total_revenue = float(sales["revenue"].sum())
        total_profit = float(sales["profit"].sum())
        margin = total_profit / total_revenue * 100 if total_revenue else 0

        st.success(
            f"Top profit-generating product: {best_product} (₹{by_product.loc[best_product, 'profit']:,.2f} "
            f"profit)."
        )
        st.info(
            f"Category contributing the most profit: {best_category}. Review "
            f"its sales and product mix to understand what drives it."
        )
        st.warning(
            f"Lowest profit among recorded products: {weakest_product} "
            f"(₹{by_product.loc[weakest_product, 'profit']:,.2f})."
        )

        if margin < 10:
            st.warning(f"Overall profit margin is {margin:.1f}%. Review costs and pricing.")
        else:
            st.write(
                f"Overall profit margin is {margin:.1f}%. Continue "
                f"monitoring this metric over time."
            )

        st.subheader("Product Performance")
        st.dataframe(by_product.reset_index(), use_container_width=True, hide_index=True)
        st.caption(
            "Recommendations are simple rule-based suggestions derived "
            "from recorded sales, not predictions from an AI model."
        )
