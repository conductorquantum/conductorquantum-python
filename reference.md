# Reference
## Models
<details><summary><code>client.models.<a href="src/conductor_quantum/models/client.py">get</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the information for a model.

Args:
model_id: The ID of the model.

Returns:
The model information.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.models.get(
    model_id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**model_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.models.<a href="src/conductor_quantum/models/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get all models.

Returns:
A list of all models.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.models.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**skip:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.models.<a href="src/conductor_quantum/models/client.py">response</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Endpoint to perform inference on a model.

Args:
request_info: The model request information.
processed_file: The processed file containing the data.
database: The database session.

Returns:
The model response.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.models.response(
    request_info="request_info",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_info:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**file:** `from __future__ import annotations

core.File` — See core.File for more documentation
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.models.<a href="src/conductor_quantum/models/client.py">turn_on_parameter_extractor_plot_input</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Endpoint to plot turn-on data from a .npy file.

Args:
data: a tensor of shape (N, 2) containing the data.
request_info: The model request information.

Returns:
The plotly figure as a JSON string.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.models.turn_on_parameter_extractor_plot_input(
    request_info="request_info",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_info:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**file:** `from __future__ import annotations

core.File` — See core.File for more documentation
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.models.<a href="src/conductor_quantum/models/client.py">create_user</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new user in the database

Args:
user: The user data to create

Returns:
The created user
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.models.create_user(
    auth0id="auth0_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**auth0id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.models.<a href="src/conductor_quantum/models/client.py">get_user_id_from_auth0id</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the user id from the auth0_id

Args:
auth0_id: The auth0_id of the user

Returns:
The user id
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.models.get_user_id_from_auth0id(
    auth0id="auth0_id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**auth0id:** `str` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.models.<a href="src/conductor_quantum/models/client.py">delete_user</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete the user account

Args:
user_id: The ID of the user

Returns:
A message indicating the success of the operation
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.models.delete_user()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Results
<details><summary><code>client.results.<a href="src/conductor_quantum/results/client.py">get_percentage_increase</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the percentage increase in the number of model results created by a user
last week compared to the week before.

Args:
database: The database session.
user: The user.

Returns:
The percentage increase.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.results.get_percentage_increase()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.results.<a href="src/conductor_quantum/results/client.py">get_model_result_count</a>()</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the total number of ModelResult belonging to a user.

Args:
database: The database session.
user: The user.

Returns:
A dictionary containing the count of ModelResult.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.results.get_model_result_count()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.results.<a href="src/conductor_quantum/results/client.py">model_info</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get a model result by ID.

Args:
model_result_id: The ID of the model result.
database: The database session.
user: The user.

Returns:
The model result and optionally the plotly JSON.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.results.model_info(
    model_result_id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**model_result_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**dark_mode:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**include_plot:** `typing.Optional[bool]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.results.<a href="src/conductor_quantum/results/client.py">delete_model_result</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a model result by ID.

Args:
model_result_id: The ID of the model result.
database: The database session.
user: The user.

Returns:
None.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.results.delete_model_result(
    model_result_id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**model_result_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.results.<a href="src/conductor_quantum/results/client.py">get_all_models_results</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get all model results.

Args:
skip: Number of model results to skip.
limit: Number of model results to return.

Returns:
List of model results.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.results.get_all_models_results()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**skip:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.results.<a href="src/conductor_quantum/results/client.py">download_model_result</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Download a model result as a JSON file zipped with the input file from GCS.

Args:
model_result_id: The ID of the model result.
database: The database session.
user: The user.

Returns:
The zipped file as bytes.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from conductor_quantum import ConductorQuantum

client = ConductorQuantum(
    base_url="https://yourhost.com/path/to/api",
)
client.results.download_model_result(
    model_result_id=1,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**model_result_id:** `int` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

