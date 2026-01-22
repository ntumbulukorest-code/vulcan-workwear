from flask import Flask, request, redirect, session, render_template_string
from datetime import datetime

app = Flask(__name__)
app.secret_key = "vulcan_secret"

# ---------------- USERS ----------------
users = {
    "zodwa": {"role": "picker", "password": "zod@123"},
    "bayanda": {"role": "picker", "password": "bay@123"},
    "mthulisi": {"role": "picker", "password": "mth@123"},
    "sibonelo": {"role": "picker", "password": "sib@123"},

    "matome": {"role": "packer", "password": "mat@123"},
    "ronica": {"role": "packer", "password": "ron@123"},
    "zelda": {"role": "packer", "password": "zel@123"},

    "nicole": {"role": "reception", "password": "nic@123"},
    "nikkie": {"role": "reception", "password": "nik@123"},

    "doctor": {"role": "driver", "password": "doc@123"},
    "thapelo": {"role": "driver", "password": "tha@123"},

    "fta": {"role": "customer", "password": "fta@123"},
    "faster": {"role": "customer", "password": "fas@123"},
    "magnate": {"role": "customer", "password": "mag@123"},
}

# ---------------- STOCK WITH COLOURS ----------------
stock = {
    "Vulcan Jacket": ["Black", "Navy", "Grey"],
    "Golf Shirt": ["Red", "Blue", "Green"],
    "Conti Suit": ["Khaki", "Navy"]
}

# ---------------- DEMO DATA RESET ----------------
def reset_demo():
    base = 80500
    data = []
    for cust in ["fta", "faster", "magnate"]:
        for i in range(5):
            data.append({
                "order": base,
                "customer": cust,
                "item": "Vulcan Jacket",
                "colour": "Black",
                "qty": 2,
                "status": "Order Processed",
                "driver": "",
                "log": []
            })
            base += 1
    return data

orders = reset_demo()
sap_queue = []

# ---------------- HTML ----------------
PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>Vulcan Workwear – Demo</title>
<style>
body{font-family:Arial;background:linear-gradient(to right,#1f4037,#99f2c8);}
.box{background:white;width:95%;max-width:1200px;margin:30px auto;padding:25px;border-radius:10px;}
h2,h3{text-align:center;}
table{width:100%;border-collapse:collapse;margin-top:15px;}
th,td{border:1px solid #ccc;padding:8px;text-align:center;}
.btn{background:#1f4037;color:white;padding:6px 12px;border-radius:5px;text-decoration:none;margin:2px;}
.btn:hover{background:#145a32;}
.notice{background:#e8f8f5;padding:10px;margin-top:10px;border-left:5px solid #1f4037;}
.center{text-align:center;margin-top:20px;}
</style>
</head>

<body>
<div class="box">

{% if page=="login" %}
<h2>Vulcan Workwear Login</h2>
<form method="post" class="center">
<input name="username" placeholder="Username"><br><br>
<input type="password" name="password" placeholder="Password"><br><br>
<button class="btn">Login</button>
</form>

{% else %}
<h2>Welcome {{user}} ({{role}})</h2>

{% if role=="customer" %}
<h3>Create Quote / Order</h3>
<form method="post" action="/create_order" class="center">

Item:
<select name="item">
{% for i in stock %}
<option value="{{i}}">{{i}}</option>
{% endfor %}
</select>

Colour:
<select name="colour">
<option>Black</option>
<option>Navy</option>
<option>Grey</option>
<option>Red</option>
<option>Blue</option>
<option>Green</option>
<option>Khaki</option>
</select>

Qty:
<input type="number" name="qty" value="1" min="1">

<button class="btn" name="type" value="Quote">Create Quote</button>
<button class="btn" name="type" value="Order">Create Order</button>
</form>
{% endif %}

<h3>Orders</h3>
<table>
<tr>
<th>Order</th><th>Customer</th><th>Item</th><th>Colour</th><th>Qty</th>
<th>Status</th><th>Driver</th><th>Actions</th>
</tr>

{% for o in orders %}
<tr>
<td>{{o.order}}</td>
<td>{{o.customer}}</td>
<td>{{o.item}}</td>
<td>{{o.colour}}</td>
<td>{{o.qty}}</td>
<td>{{o.status}}</td>
<td>{{o.driver}}</td>
<td>
{% if role=="picker" and o.status=="Order Processed" %}
<a class="btn" href="/update/{{o.order}}/pick">Pick</a>{% endif %}

{% if role=="packer" and o.status=="Picked" %}
<a class="btn" href="/update/{{o.order}}/pack">Pack</a>{% endif %}

{% if role=="reception" and o.status=="Packed" %}
<a class="btn" href="/update/{{o.order}}/invoice">Invoice</a>{% endif %}

{% if role=="driver" and o.status=="Ready for Collection" %}
<a class="btn" href="/update/{{o.order}}/dispatch">Dispatch</a>{% endif %}

{% if role=="driver" and o.status=="Out for Delivery" %}
<a class="btn" href="/update/{{o.order}}/deliver">Deliver</a>{% endif %}
</td>
</tr>
{% endfor %}
</table>

{% if role=="reception" %}
<h3>SAP Mock – Invoiced Orders</h3>
<table>
<tr><th>Order</th><th>Customer</th><th>Item</th><th>Qty</th></tr>
{% for s in sap %}
<tr><td>{{s.order}}</td><td>{{s.customer}}</td><td>{{s.item}}</td><td>{{s.qty}}</td></tr>
{% endfor %}
</table>
{% endif %}

{% if notice %}
<div class="notice">{{notice}}</div>
{% endif %}

<div class="center">
<a class="btn" href="/reset">Reset Demo</a>
<a class="btn" href="/logout">Logout</a>
</div>
{% endif %}

</div>
</body>
</html>
"""

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"].lower()
        p=request.form["password"]
        if u in users and users[u]["password"]==p:
            session["user"]=u
            session["role"]=users[u]["role"]
            return redirect("/dashboard")
    return render_template_string(PAGE,page="login")

@app.route("/dashboard")
def dashboard():
    role=session.get("role")
    user=session.get("user")
    view_orders = [o for o in orders if o["customer"]==user] if role=="customer" else orders

    return render_template_string(
        PAGE,page="dash",
        user=user,
        role=role,
        orders=view_orders,
        stock=stock,
        sap=sap_queue,
        notice=session.pop("notice",None)
    )

@app.route("/create_order", methods=["POST"])
def create_order():
    new_no = orders[-1]["order"] + 1
    orders.append({
        "order": new_no,
        "customer": session["user"],
        "item": request.form["item"],
        "colour": request.form["colour"],
        "qty": request.form["qty"],
        "status": "Order Processed",
        "driver": "",
        "log": [f"Created {datetime.now()}"]
    })
    session["notice"] = "📧 Email sent | 💬 WhatsApp notification sent"
    return redirect("/dashboard")

@app.route("/update/<int:o>/<action>")
def update(o,action):
    for x in orders:
        if x["order"]==o:
            if action=="pick": x["status"]="Picked"
            elif action=="pack": x["status"]="Packed"
            elif action=="invoice":
                x["status"]="Ready for Collection"
                sap_queue.append(x)
                session["notice"]="📧 Invoiced | 💬 Customer notified"
            elif action=="dispatch":
                x["status"]="Out for Delivery"
                x["driver"]=session["user"]
            elif action=="deliver":
                x["status"]="Delivered (POD Uploaded)"
                session["notice"]="📧 POD received | 💬 Delivery confirmation sent"
    return redirect("/dashboard")

@app.route("/reset")
def reset():
    global orders, sap_queue
    orders = reset_demo()
    sap_queue = []
    session["notice"] = "Demo reset completed"
    return redirect("/dashboard")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# THIS LINE IS CRITICAL FOR DEPLOYMENT:
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)