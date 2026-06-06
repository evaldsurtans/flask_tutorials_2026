const { useState, useEffect } = React;

function Tags({searchUrl}) {

    const [response, setResponse] = useState([]);

    useEffect(() => {
        console.log("gethi")
        searchTags();
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const input = formData.get("filters");

        searchTags(input);
    }

    const searchTags = async (input?) => {

        try {
            const response = await axios.get(`${searchUrl}/search`, { //might be magic, also hardcoded
                params: { filter: input }
            });

            setResponse(response.data);
        }
        catch (e) {
            return "error"
        }
    }

    return (
        <div className="flex flex-col w-full items-center justify-center mt-30">
            <label className="input input-primary">
                <i className="fa-solid fa-magnifying-glass"></i>
                <form onSubmit={handleSubmit}>
                    <input
                        name="filters"
                        type="text"
                        placeholder="Filter by tag name"
                        onInput={(e) => e.currentTarget.form.requestSubmit()}
                    />
                </form>
            </label>

            <div className="flex flex-wrap justify-center w-full mt-20" style={{ gap: '1rem' }} id="results-container">
                <TagCards tags={response}/>
            </div>
        </div>
    );
}

function TagCards({tags}) {
    return (
        tags.map((tag) => (
            <div key={tag.tag_id} className="card w-96 bg-base-100 card-md shadow-sm">
                <div className="card-body">
                    <h2 className="card-title">{tag.tag_name}</h2>
                    <p>Created: {tag.created}</p>
                    <a href={tag.tag_url} className="btn btn-square btn-ghost">
                        <i className="fa-solid fa-pen-clip"></i>
                    </a>
                </div>
            </div>
        ))
    )
}