# Reference
## models
<details><summary><code>client.models.<a href="src/conductorquantum/models/client.py">info</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves a model's details.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.models.info(
    model="coulomb-blockade-peak-detector-v1",
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

**model:** `str` — The model to get information for.
    
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

<details><summary><code>client.models.<a href="src/conductorquantum/models/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves a list of available models.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.models.list(
    skip=1,
    limit=1,
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

**skip:** `typing.Optional[int]` — The number of models to skip.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — The number of models to include.
    
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

<details><summary><code>client.models.<a href="src/conductorquantum/models/client.py">execute</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Analyze your input data using the specified model. For more information about available models and their capabilities, see our [overview](/models/overview).
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.models.execute(
    model="model",
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

**model:** `str` — The model to run.
    
</dd>
</dl>

<dl>
<dd>

**data:** `from __future__ import annotations

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

## ModelResults
<details><summary><code>client.model_results.<a href="src/conductorquantum/model_results/client.py">vote_on_model_result</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create or update a vote on a model result.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.model_results.vote_on_model_result(
    result_id="result_id",
    vote=1,
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

**result_id:** `str` — The UUID of the model result.
    
</dd>
</dl>

<dl>
<dd>

**vote:** `int` — 1 for upvote, -1 for downvote
    
</dd>
</dl>

<dl>
<dd>

**feedback:** `typing.Optional[str]` — Optional text feedback
    
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

<details><summary><code>client.model_results.<a href="src/conductorquantum/model_results/client.py">remove_vote_on_model_result</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Remove a user's vote on a model result.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.model_results.remove_vote_on_model_result(
    result_id="result_id",
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

**result_id:** `str` — The UUID of the model result.
    
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

<details><summary><code>client.model_results.<a href="src/conductorquantum/model_results/client.py">info</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves a model result.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.model_results.info(
    id="08047949-7263-4557-9122-ab293a49cae5",
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

**id:** `str` — The UUID of the model result.
    
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

<details><summary><code>client.model_results.<a href="src/conductorquantum/model_results/client.py">delete</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a model result.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.model_results.delete(
    id="08047949-7263-4557-9122-ab293a49cae5",
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

**id:** `str` — The UUID of the model result.
    
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

<details><summary><code>client.model_results.<a href="src/conductorquantum/model_results/client.py">list</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves a list of model results.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.model_results.list(
    skip=1,
    limit=1,
    model_str_id="model_str_id",
    start_date="start_date",
    end_date="end_date",
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

**skip:** `typing.Optional[int]` — The number of model results to skip.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — The number of model results to include.
    
</dd>
</dl>

<dl>
<dd>

**model_str_id:** `typing.Optional[str]` — Filter by model str_id.
    
</dd>
</dl>

<dl>
<dd>

**start_date:** `typing.Optional[str]` — Filter results created on or after this date.
    
</dd>
</dl>

<dl>
<dd>

**end_date:** `typing.Optional[str]` — Filter results created on or before this date.
    
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

<details><summary><code>client.model_results.<a href="src/conductorquantum/model_results/client.py">download</a>(...)</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Downloads a model result as a JSON file zipped with the input file.
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
from conductorquantum import ConductorQuantum

client = ConductorQuantum(
    token="YOUR_TOKEN",
)
client.model_results.download(
    id="id",
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

**id:** `str` — The UUID of the model result.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration. You can pass in configuration such as `chunk_size`, and more to customize the request and response.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

